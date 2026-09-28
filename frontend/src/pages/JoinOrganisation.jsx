import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import api from "../services/api";

function JoinOrganisation() {
    const navigate = useNavigate();

    const { register } = useAuth();

    const [organisations, setOrganisations] = useState([]);
    const [departments, setDepartments] = useState([]);

    const [organisationId, setOrganisationId] = useState("");
    const [role, setRole] = useState("user");
    const [departmentId, setDepartmentId] = useState("");

    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);
    const [loadingDepartments, setLoadingDepartments] =
        useState(false);

    // --------------------------------------------------
    // Load organisations
    // --------------------------------------------------

    useEffect(() => {
        const loadOrganisations = async () => {
            try {
                const response =
                    await api.get("/organisations");

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

    // --------------------------------------------------
    // Organisation changed
    // --------------------------------------------------

    const handleOrganisationChange = async (id) => {
        setOrganisationId(id);

        // Reset department whenever organisation changes
        setDepartmentId("");
        setDepartments([]);

        if (!id) {
            return;
        }

        // Only need departments for support agents
        if (role !== "support_agent") {
            return;
        }

        await loadDepartments(id);
    };

    // --------------------------------------------------
    // Load departments
    // --------------------------------------------------

    const loadDepartments = async (organisationId) => {
        try {
            setLoadingDepartments(true);

            /*
             * IMPORTANT:
             *
             * This endpoint must be PUBLIC because the user
             * is not logged in yet.
             *
             * Example:
             *
             * GET /organisations/{organisation_id}/departments
             */

            const response = await api.get(
                `/organisations/${organisationId}/departments`
            );

            setDepartments(response.data);

        } catch (error) {
            console.error(error);

            setError(
                "Unable to load departments."
            );

        } finally {
            setLoadingDepartments(false);
        }
    };

    // --------------------------------------------------
    // Role changed
    // --------------------------------------------------

    const handleRoleChange = async (newRole) => {
        setRole(newRole);

        // Normal users don't have departments
        if (newRole === "user") {
            setDepartmentId("");
            return;
        }

        // Support agent
        if (
            newRole === "support_agent" &&
            organisationId
        ) {
            await loadDepartments(
                organisationId
            );
        }
    };

    // --------------------------------------------------
    // Register
    // --------------------------------------------------

    const handleSubmit = async (e) => {
        e.preventDefault();

        setError("");

        // ------------------------------------------
        // Validation
        // ------------------------------------------

        if (!organisationId) {
            setError(
                "Please select an organisation."
            );
            return;
        }

        if (
            role === "support_agent" &&
            !departmentId
        ) {
            setError(
                "Please select a department."
            );
            return;
        }

        setLoading(true);

        try {
            const result = await register({
                name,
                email,
                password,

                organisation_id:
                    organisationId,

                role,

                // VERY IMPORTANT:
                // null, NOT "null"
                department_id:
                    role === "support_agent"
                        ? departmentId
                        : null,
            });

            console.log(
                "Registration successful:",
                result
            );

            alert(
                "Account created successfully."
            );

            // --------------------------------------
            // Decide where user goes after register
            // --------------------------------------

            if (role === "user") {
                navigate("/dashboard");
            } else if (
                role === "support_agent"
            ) {
                navigate("/dashboard");
            }

        } catch (error) {
            console.error(
                "Registration failed:",
                error
            );

            const message =
                error.response?.data?.detail ||
                "Unable to create account.";

            setError(message);

        } finally {
            setLoading(false);
        }
    };

    // --------------------------------------------------
    // UI
    // --------------------------------------------------

    return (
        <div className="auth-page">

            <div className="auth-card">

                <div className="page-top">
                    <button
                        className="back-button"
                        onClick={() =>
                            navigate("/login")
                        }
                    >
                        ← Back
                    </button>
                </div>

                <div className="brand">

                    <div className="brand-icon">
                        O
                    </div>

                    <div>
                        <h1>OneDesk AI</h1>

                        <p>
                            Join an organisation
                        </p>
                    </div>

                </div>

                <div className="auth-heading">

                    <h2>
                        Join Organisation
                    </h2>

                    <p>
                        Create your account and
                        join an existing organisation.
                    </p>

                </div>

                <form
                    onSubmit={handleSubmit}
                >

                    {/* NAME */}

                    <div className="form-group">

                        <label>
                            Your Name
                        </label>

                        <input
                            type="text"
                            placeholder="Your name"
                            value={name}
                            onChange={(e) =>
                                setName(
                                    e.target.value
                                )
                            }
                            required
                        />

                    </div>

                    {/* EMAIL */}

                    <div className="form-group">

                        <label>
                            Email
                        </label>

                        <input
                            type="email"
                            placeholder="you@example.com"
                            value={email}
                            onChange={(e) =>
                                setEmail(
                                    e.target.value
                                )
                            }
                            required
                        />

                    </div>

                    {/* PASSWORD */}

                    <div className="form-group">

                        <label>
                            Password
                        </label>

                        <input
                            type="password"
                            placeholder="Minimum 8 characters"
                            value={password}
                            onChange={(e) =>
                                setPassword(
                                    e.target.value
                                )
                            }
                            minLength={8}
                            required
                        />

                    </div>

                    {/* ORGANISATION */}

                    <div className="form-group">

                        <label>
                            Organisation
                        </label>

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
                                        key={
                                            organisation.id
                                        }
                                        value={
                                            organisation.id
                                        }
                                    >
                                        {
                                            organisation.name
                                        }
                                    </option>
                                )
                            )}

                        </select>

                    </div>

                    {/* ROLE */}

                    <div className="form-group">

                        <label>
                            Role
                        </label>

                        <div className="role-options">

                            <label>

                                <input
                                    type="radio"
                                    value="user"
                                    checked={
                                        role ===
                                        "user"
                                    }
                                    onChange={() =>
                                        handleRoleChange(
                                            "user"
                                        )
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
                                    onChange={() =>
                                        handleRoleChange(
                                            "support_agent"
                                        )
                                    }
                                />

                                Support Agent

                            </label>

                        </div>

                    </div>

                    {/* DEPARTMENT */}

                    {role === "support_agent" && (

                        <div className="form-group">

                            <label>
                                Department
                            </label>

                            <select
                                value={
                                    departmentId
                                }
                                onChange={(e) =>
                                    setDepartmentId(
                                        e.target.value
                                    )
                                }
                                required
                                disabled={
                                    loadingDepartments
                                }
                            >

                                <option value="">
                                    {loadingDepartments
                                        ? "Loading departments..."
                                        : "Select department"}
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
                                            {
                                                department.name
                                            }
                                        </option>

                                    )
                                )}

                            </select>

                        </div>

                    )}

                    {/* ERROR */}

                    {error && (

                        <div className="error-message">
                            {error}
                        </div>

                    )}

                    {/* SUBMIT */}

                    <button
                        className="primary-button"
                        type="submit"
                        disabled={
                            loading ||
                            loadingDepartments
                        }
                    >
                        {loading
                            ? "Creating account..."
                            : "Create Account"}
                    </button>

                </form>

                <p className="bottom-text">

                    Already have an account?{" "}

                    <button
                        className="inline-link"
                        onClick={() =>
                            navigate("/login")
                        }
                    >
                        Sign in
                    </button>

                </p>

            </div>

        </div>
    );
}

export default JoinOrganisation;