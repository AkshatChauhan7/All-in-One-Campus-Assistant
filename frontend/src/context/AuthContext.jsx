import { createContext, useContext, useEffect, useState } from "react";
import api from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [token, setToken] = useState(
        localStorage.getItem("access_token")
    );

    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    // Get current user if a token already exists
    useEffect(() => {
        const loadUser = async () => {
            if (!token) {
                setLoading(false);
                return;
            }

            try {
                const response = await api.get("/auth/me", {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });

                setUser(response.data);
            } catch (error) {
                console.error("Authentication failed:", error);

                localStorage.removeItem("access_token");
                setToken(null);
                setUser(null);
            } finally {
                setLoading(false);
            }
        };

        loadUser();
    }, [token]);

    // Login
    const login = async (email, password) => {
        const response = await api.post("/auth/login", {
            email,
            password,
        });

        const accessToken = response.data.access_token;

        localStorage.setItem("access_token", accessToken);
        setToken(accessToken);

        return accessToken;
    };

    // Logout
    const logout = () => {
        localStorage.removeItem("access_token");
        setToken(null);
        setUser(null);
    };

    const value = {
        token,
        user,
        loading,
        login,
        logout,
        isAuthenticated: !!token,
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    return useContext(AuthContext);
}