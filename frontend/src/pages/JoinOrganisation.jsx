import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

function JoinOrganisation() {
    const navigate = useNavigate();

    const [organisations, setOrganisations] = useState([]);

    const [organisationId, setOrganisationId] = useState("");
    const [role, setRole] = useState("user");
    const [departmentId, setDepartmentId] = useState("");

    const [departments, setDepartments] = useState([]);

    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        const loadOrganisations = async () => {
            try {
                const response = await api.get("/organisations");

                setOrganisations(response.data);
            } catch (error) {
                console.error(error);

                setError(
                    "Unable to load organisations."
                );
            }
        };

        loadOrganisations();
    }, []);

    const handleOrganisationChange = async (id) => {
        setOrganisationId(id);
        setDepartmentId("");

        if (!id) {
            setDepartments([]);
            return;
        }

        try {
            /*
             * Current backend /departments uses the
             * logged-in user's organisation, so it cannot
             * yet fetch departments for an organisation
             * before login.
             *
             * We will add a public endpoint for this later.
             */
            setDepartments([]);

        } catch (error) {
            console.error(error);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        setError("");
        setLoading(true);

        try {
            /*
             * This endpoint expects an authenticated user
             * in our current backend.
             *
             * The complete registration + join flow will
             * be connected when we add the public join API.
             */
            await api.post("/join-requests", {
                organisation_id: organisationId,
                role,
                department_id:
                    role === "support_agent"
                        ? departmentId
                        : null,
            });

            alert(
                "Join request submitted successfully."
            );

            navigate("/login");

        } catch (error) {
            const message =
                error.response?.data?.detail ||
                "Unable to submit join request.";

            setError(message);

        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-page">

            <div className="auth-card">

                <div className="page-top">
                    <button
                        className="back-button"
                        onClick={() => navigate("/login")}
                    >
                        ← Back
                    </button>
                </div>

                <div className="brand">
                    <div className="brand-icon">O</div>

                    <div>
                        <h1>OneDesk AI</h1>
                        <p>Join an organisation</p>
                    </div>
                </div>

                <div className="auth-heading">
                    <h2>Join Organisation</h2>

                    <p>
                        Request access to an existing
                        organisation.
                    </p>
                </div>

                <form onSubmit={handleSubmit}>

                    <div className="form-group">
                        <label>Your Name</label>

                        <input
                            type="text"
                            placeholder="Your name"
                            value={name}
                            onChange={(e) =>
                                setName(e.target.value)
                            }
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label>Email</label>

                        <input
                            type="email"
                            placeholder="you@example.com"
                            value={email}
                            onChange={(e) =>
                                setEmail(e.target.value)
                            }
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label>Password</label>

                        <input
                            type="password"
                            placeholder="Minimum 8 characters"
                            value={password}
                            onChange={(e) =>
                                setPassword(e.target.value)
                            }
                            minLength={8}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label>Organisation</label>

                        <select
                            value={organisationId}
                            onChange={(e) =>
                                handleOrganisationChange(
                                    e.target.value
                                )
                            }
                            required
                        >
                            <option value="">
                                Select organisation
                            </option>

                            {organisations.map(
                                (organisation) => (
                                    <option
                                        key={organisation.id}
                                        value={organisation.id}
                                    >
                                        {organisation.name}
                                    </option>
                                )
                            )}
                        </select>
                    </div>

                    <div className="form-group">

                        <label>Role</label>

                        <div className="role-options">

                            <label>
                                <input
                                    type="radio"
                                    value="user"
                                    checked={role === "user"}
                                    onChange={(e) =>
                                        setRole(e.target.value)
                                    }
                                />

                                User
                            </label>

                            <label>
                                <input
                                    type="radio"
                                    value="support_agent"
                                    checked={
                                        role ===
                                        "support_agent"
                                    }
                                    onChange={(e) =>
                                        setRole(e.target.value)
                                    }
                                />

                                Support Agent
                            </label>

                        </div>

                    </div>

                    {role === "support_agent" && (
                        <div className="form-group">

                            <label>Department</label>

                            <select
                                value={departmentId}
                                onChange={(e) =>
                                    setDepartmentId(
                                        e.target.value
                                    )
                                }
                                required
                            >
                                <option value="">
                                    Select department
                                </option>

                                {departments.map(
                                    (department) => (
                                        <option
                                            key={
                                                department.id
                                            }
                                            value={
                                                department.id
                                            }
                                        >
                                            {department.name}
                                        </option>
                                    )
                                )}
                            </select>

                        </div>
                    )}

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
                        {loading
                            ? "Submitting..."
                            : "Send Join Request"}
                    </button>

                </form>

                <p className="bottom-text">
                    Want to create your own organisation?{" "}
                    <button
                        className="inline-link"
                        onClick={() =>
                            navigate(
                                "/create-organisation"
                            )
                        }
                    >
                        Create one
                    </button>
                </p>

            </div>

        </div>
    );
}

export default JoinOrganisation;