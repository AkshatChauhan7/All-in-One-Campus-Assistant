import { createContext, useContext, useEffect, useState } from "react";
import api from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [token, setToken] = useState(
        localStorage.getItem("access_token")
    );

    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    // --------------------------------------------------
    // Load logged-in user
    // --------------------------------------------------

    useEffect(() => {
        const loadUser = async () => {
            if (!token) {
                setLoading(false);
                return;
            }

            try {
                const response = await api.get("/auth/me");

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

    // --------------------------------------------------
    // Login
    // --------------------------------------------------

    const login = async (email, password) => {
        const response = await api.post("/auth/login", {
            email,
            password,
        });

        const accessToken = response.data.access_token;

        localStorage.setItem(
            "access_token",
            accessToken
        );

        setToken(accessToken);

        // Fetch complete user information
        const userResponse = await api.get("/auth/me");

        setUser(userResponse.data);

        return userResponse.data;
    };

    // --------------------------------------------------
    // Register
    // --------------------------------------------------

    const register = async ({
        name,
        email,
        password,
        organisation_id,
        role,
        department_id,
    }) => {
        const response = await api.post("/auth/register", {
            name,
            email,
            password,
            organisation_id,
            role,
            department_id:
                role === "support_agent"
                    ? department_id
                    : null,
        });

        return response.data;
    };

    // --------------------------------------------------
    // Logout
    // --------------------------------------------------

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
        register,
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