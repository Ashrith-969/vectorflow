package com.vectorflow.service;

import com.vectorflow.model.Role;
import com.vectorflow.model.User;
import com.vectorflow.repository.UserRepository;
import com.vectorflow.security.JwtTokenProvider;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtTokenProvider jwtTokenProvider;

    public AuthResult register(String email, String password) {
        if (userRepository.existsByEmail(email)) {
            throw new RuntimeException("User with this email already exists");
        }

        User user = User.builder()
                .email(email)
                .passwordHash(passwordEncoder.encode(password))
                .role(Role.VIEWER)
                .build();

        user = userRepository.save(user);
        log.info("Registered user {} with role {}", user.getEmail(), user.getRole());

        String token = jwtTokenProvider.generateToken(user.getEmail(), user.getRole().name());

        return new AuthResult(token, user);
    }

    public AuthResult login(String email, String password) {
        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("Invalid credentials"));

        if (!passwordEncoder.matches(password, user.getPasswordHash())) {
            throw new RuntimeException("Invalid credentials");
        }

        String token = jwtTokenProvider.generateToken(user.getEmail(), user.getRole().name());
        log.info("User {} logged in with role {}", user.getEmail(), user.getRole());

        return new AuthResult(token, user);
    }

    public User assignRole(String userId, String roleName) {
        Role role;
        try {
            role = Role.valueOf(roleName.toUpperCase());
        } catch (IllegalArgumentException e) {
            throw new RuntimeException("Invalid role: " + roleName + ". Valid roles: VIEWER, EDITOR, ADMIN");
        }

        User user = userRepository.findById(UUID.fromString(userId))
                .orElseThrow(() -> new RuntimeException("User not found with id: " + userId));

        user.setRole(role);
        user = userRepository.save(user);
        log.info("Role updated: user={}, newRole={}", user.getEmail(), user.getRole());

        return user;
    }

    public record AuthResult(String token, User user) {}
}
