package com.vectorflow.security;

import com.vectorflow.model.Role;
import com.vectorflow.model.User;
import com.vectorflow.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.stereotype.Component;

import java.util.Arrays;
import java.util.stream.Collectors;

/**
 * Centralized authentication + authorization guard for GraphQL resolvers.
 *
 * Usage in resolvers:
 *   User user = authGuard.requireAuth();                                 // authenticated only
 *   User user = authGuard.requireRole(Role.ADMIN);                       // single role
 *   User user = authGuard.requireAnyRole(Role.EDITOR, Role.ADMIN);       // any of listed roles
 *   User user = authGuard.optionalAuth();                                // nullable
 */
@Component
@RequiredArgsConstructor
@Slf4j
public class GraphQlAuthGuard {

    private final UserRepository userRepository;

    /**
     * Require a valid authenticated user.
     */
    public User requireAuth() {
        User user = resolve();
        if (user == null) {
            throw new AccessDeniedException("Authentication required. Please provide a valid JWT token.");
        }
        return user;
    }

    /**
     * Require an authenticated user with exactly the given role.
     */
    public User requireRole(Role required) {
        User user = requireAuth();
        if (user.getRole() != required) {
            throw new AccessDeniedException(
                    "Access denied. Required role: " + required.name() + ", your role: " + user.getRole().name());
        }
        return user;
    }

    /**
     * Require an authenticated user with any of the given roles.
     */
    public User requireAnyRole(Role... allowed) {
        User user = requireAuth();
        for (Role role : allowed) {
            if (user.getRole() == role) {
                return user;
            }
        }
        String allowedStr = Arrays.stream(allowed).map(Role::name).collect(Collectors.joining(", "));
        throw new AccessDeniedException(
                "Access denied. Required one of: [" + allowedStr + "], your role: " + user.getRole().name());
    }

    /**
     * Return the authenticated user if present, or null for anonymous access.
     */
    public User optionalAuth() {
        return resolve();
    }

    private User resolve() {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        if (auth != null && auth.getPrincipal() instanceof UserDetails userDetails) {
            log.debug("Authenticated user: {}", userDetails.getUsername());
            return userRepository.findByEmail(userDetails.getUsername()).orElse(null);
        }
        return null;
    }
}
