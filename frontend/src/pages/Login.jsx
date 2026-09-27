import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import api from "../services/api";

function Login() {
    const navigate = useNavigate();
    const { login } = useAuth();

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();

        setError("");
        setLoading(true);

        try {
            await login(email, password);
            const userResponse = await api.get("/auth/me", {
                headers: {
                    Authorization: `Bearer ${localStorage.getItem("access_token")}`,
                },
            });

            const loggedInUser = userResponse.data;

            if (loggedInUser.role === "platform_admin") {
                navigate("/platform-admin");
            } else {
                navigate("/dashboard");
            }
            // await login(email, password);
            // navigate("/dashboard");
        } catch (error) {
            const message =
                error.response?.data?.detail ||
                "Invalid email or password.";

            setError(message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-page">

            <div className="auth-card">

                <div className="brand">
                    <div className="brand-icon">O</div>

                    <div>
                        <h1>OneDesk AI</h1>
                        <p>One Front Door for Everything</p>
                    </div>
                </div>

                <div className="auth-heading">
                    <h2>Welcome back</h2>
                    <p>Sign in to continue to your organisation.</p>
                </div>

                <form onSubmit={handleSubmit}>

                    <div className="form-group">
                        <label>Email</label>

                        <input
                            type="email"
                            placeholder="you@example.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label>Password</label>

                        <input
                            type="password"
                            placeholder="Enter your password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>

                    {error && (
                        <div className="error-message">
                            {error}
                        </div>
                    )}

                    <button
                        className="primary-button"
                        type="submit"
                        disabled={loading}
                    >
                        {loading ? "Signing in..." : "Sign In"}
                    </button>

                </form>

                <div className="divider">
                    <span>OR</span>
                </div>

                <button
                    className="secondary-button"
                    onClick={() => navigate("/create-organisation")}
                >
                    Create Organisation
                </button>

                <button
                    className="link-button"
                    onClick={() => navigate("/join-organisation")}
                >
                    Want to join an existing organisation?
                </button>

            </div>

        </div>
    );
}

export default Login;