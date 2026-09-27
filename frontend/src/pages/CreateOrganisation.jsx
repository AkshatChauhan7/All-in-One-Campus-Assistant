import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

const defaultDepartments = [
    "IT",
    "HR",
    "Finance",
    "Facilities",
    "Administration",
];

function CreateOrganisation() {
    const navigate = useNavigate();

    const [organisationName, setOrganisationName] = useState("");
    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    const [departments, setDepartments] = useState(
        defaultDepartments.map((name) => ({
            name,
            selected: false,
            bot_enabled: true,
            human_support_enabled: true,
        }))
    );

    const [customDepartment, setCustomDepartment] = useState("");

    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const toggleDepartment = (index) => {
        setDepartments((previous) =>
            previous.map((department, i) =>
                i === index
                    ? {
                        ...department,
                        selected: !department.selected,
                    }
                    : department
            )
        );
    };

    const addCustomDepartment = () => {
        const name = customDepartment.trim();

        if (!name) return;

        const exists = departments.some(
            (department) =>
                department.name.toLowerCase() === name.toLowerCase()
        );

        if (exists) {
            setError("This department already exists.");
            return;
        }

        setDepartments((previous) => [
            ...previous,
            {
                name,
                selected: true,
                bot_enabled: true,
                human_support_enabled: true,
            },
        ]);

        setCustomDepartment("");
        setError("");
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        setError("");
        setLoading(true);

        try {
            const selectedDepartments = departments
                .filter((department) => department.selected)
                .map((department) => ({
                    name: department.name,
                    bot_enabled: department.bot_enabled,
                    human_support_enabled:
                        department.human_support_enabled,
                }));

            const response = await api.post(
                "/organisations/create",
                {
                    organisation_name: organisationName,
                    name,
                    email,
                    password,
                    departments: selectedDepartments,
                }
            );

            localStorage.setItem(
                "access_token",
                response.data.access_token
            );

            navigate("/dashboard");

        } catch (error) {
            const message =
                error.response?.data?.detail ||
                "Unable to create organisation.";

            setError(message);

        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-page">

            <div className="auth-card large-card">

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
                        <p>Create your organisation</p>
                    </div>
                </div>

                <div className="auth-heading">
                    <h2>Create Organisation</h2>
                    <p>
                        Set up your organisation and choose the
                        departments you need.
                    </p>
                </div>

                <form onSubmit={handleSubmit}>

                    <div className="form-group">
                        <label>Organisation Name</label>

                        <input
                            type="text"
                            placeholder="e.g. Bennett University"
                            value={organisationName}
                            onChange={(e) =>
                                setOrganisationName(e.target.value)
                            }
                            required
                        />
                    </div>

                    <div className="form-row">

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

                    <div className="department-section">

                        <div className="section-heading">
                            <h3>Departments</h3>

                            <p>
                                Select the departments your
                                organisation will use.
                            </p>
                        </div>

                        <div className="department-grid">

                            {departments.map(
                                (department, index) => (
                                    <label
                                        className={`department-option ${
                                            department.selected
                                                ? "selected"
                                                : ""
                                        }`}
                                        key={department.name}
                                    >
                                        <input
                                            type="checkbox"
                                            checked={
                                                department.selected
                                            }
                                            onChange={() =>
                                                toggleDepartment(index)
                                            }
                                        />

                                        <span>
                                            {department.name}
                                        </span>
                                    </label>
                                )
                            )}

                        </div>

                    </div>

                    <div className="custom-department">

                        <input
                            type="text"
                            placeholder="Add custom department"
                            value={customDepartment}
                            onChange={(e) =>
                                setCustomDepartment(e.target.value)
                            }
                        />

                        <button
                            type="button"
                            className="secondary-button small"
                            onClick={addCustomDepartment}
                        >
                            + Add
                        </button>

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
                        {loading
                            ? "Creating..."
                            : "Create Organisation"}
                    </button>

                </form>

                <p className="bottom-text">
                    Already have an account?{" "}
                    <button
                        className="inline-link"
                        onClick={() => navigate("/login")}
                    >
                        Sign in
                    </button>
                </p>

            </div>

        </div>
    );
}

export default CreateOrganisation;