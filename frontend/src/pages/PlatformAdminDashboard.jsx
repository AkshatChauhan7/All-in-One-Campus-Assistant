import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";
import { useAuth } from "../context/AuthContext";

function PlatformAdminDashboard() {
    const navigate = useNavigate();
    const { user, logout, token } = useAuth();

    const [organisations, setOrganisations] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const loadOrganisations = async () => {
        try {
            setLoading(true);
            setError("");

            const response = await api.get(
                "/platform-admin/organisations",
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                }
            );

            setOrganisations(response.data);
        } catch (error) {
            console.error(error);

            setError(
                error.response?.data?.detail ||
                "Unable to load organisations."
            );
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (token) {
            loadOrganisations();
        }
    }, [token]);

    const updateOrganisation = async (
        organisationId,
        action
    ) => {
        try {
            setError("");

            await api.post(
                `/platform-admin/organisations/${organisationId}/${action}`,
                {},
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                }
            );

            await loadOrganisations();

        } catch (error) {
            console.error(error);

            setError(
                error.response?.data?.detail ||
                `Unable to ${action} organisation.`
            );
        }
    };

    const handleLogout = () => {
        logout();
        navigate("/login");
    };

    const total = organisations.length;

    const pending = organisations.filter(
        (org) => org.status === "pending"
    ).length;

    const active = organisations.filter(
        (org) => org.status === "active"
    ).length;

    const rejected = organisations.filter(
        (org) => org.status === "rejected"
    ).length;

    const suspended = organisations.filter(
        (org) => org.status === "suspended"
    ).length;

    const pendingOrganisations = organisations.filter(
        (org) => org.status === "pending"
    );

    return (
        <div className="admin-layout">

            {/* Sidebar */}

            <aside className="admin-sidebar">

                <div className="sidebar-brand">
                    <div className="brand-icon">
                        O
                    </div>

                    <div>
                        <strong>OneDesk AI</strong>
                        <span>Platform</span>
                    </div>
                </div>

                <nav className="sidebar-nav">

                    <button className="sidebar-item active">
                        <span>▦</span>
                        Dashboard
                    </button>

                    <button className="sidebar-item">
                        <span>▣</span>
                        Organisations
                    </button>

                </nav>

                <button
                    className="sidebar-logout"
                    onClick={handleLogout}
                >
                    <span>↪</span>
                    Sign out
                </button>

            </aside>


            {/* Main */}

            <main className="admin-main">

                {/* Header */}

                <header className="admin-header">

                    <div>
                        <h1>Platform Dashboard</h1>

                        <p>
                            Manage organisations across
                            OneDesk AI.
                        </p>
                    </div>

                    <div className="admin-user">

                        <div className="avatar">
                            {user?.name
                                ?.charAt(0)
                                ?.toUpperCase()}
                        </div>

                        <div>
                            <strong>
                                {user?.name}
                            </strong>

                            <span>
                                Platform Admin
                            </span>
                        </div>

                    </div>

                </header>


                {/* Error */}

                {error && (
                    <div className="admin-error">
                        {error}
                    </div>
                )}


                {/* Statistics */}

                <section className="stats-grid">

                    <div className="stat-card">
                        <span>Total Organisations</span>
                        <strong>{total}</strong>
                    </div>

                    <div className="stat-card">
                        <span>Active</span>
                        <strong>{active}</strong>
                    </div>

                    <div className="stat-card pending-stat">
                        <span>Pending</span>
                        <strong>{pending}</strong>
                    </div>

                    <div className="stat-card">
                        <span>Rejected</span>
                        <strong>{rejected}</strong>
                    </div>

                    <div className="stat-card">
                        <span>Suspended</span>
                        <strong>{suspended}</strong>
                    </div>

                </section>


                {/* Pending Organisations */}

                <section className="admin-section">

                    <div className="section-header">

                        <div>
                            <h2>
                                Pending Organisations
                            </h2>

                            <p>
                                Organisations waiting for
                                platform approval.
                            </p>
                        </div>

                        <button
                            className="refresh-button"
                            onClick={loadOrganisations}
                        >
                            ↻ Refresh
                        </button>

                    </div>


                    {loading ? (

                        <div className="empty-card">
                            Loading organisations...
                        </div>

                    ) : pendingOrganisations.length === 0 ? (

                        <div className="empty-card">
                            <div className="empty-icon">
                                ✓
                            </div>

                            <h3>
                                No pending organisations
                            </h3>

                            <p>
                                All organisation requests
                                have been reviewed.
                            </p>
                        </div>

                    ) : (

                        <div className="organisation-list">

                            {pendingOrganisations.map(
                                (organisation) => (

                                    <div
                                        className="organisation-card"
                                        key={organisation.id}
                                    >

                                        <div className="organisation-info">

                                            <div className="organisation-icon">
                                                {organisation.name
                                                    .charAt(0)
                                                    .toUpperCase()}
                                            </div>

                                            <div>
                                                <h3>
                                                    {
                                                        organisation.name
                                                    }
                                                </h3>

                                                <p>
                                                    Created{" "}
                                                    {new Date(
                                                        organisation.created_at
                                                    ).toLocaleDateString()}
                                                </p>
                                            </div>

                                        </div>


                                        <div className="organisation-actions">

                                            <span className="status-badge pending">
                                                Pending
                                            </span>

                                            <button
                                                className="approve-button"
                                                onClick={() =>
                                                    updateOrganisation(
                                                        organisation.id,
                                                        "approve"
                                                    )
                                                }
                                            >
                                                Approve
                                            </button>

                                            <button
                                                className="reject-button"
                                                onClick={() =>
                                                    updateOrganisation(
                                                        organisation.id,
                                                        "reject"
                                                    )
                                                }
                                            >
                                                Reject
                                            </button>

                                        </div>

                                    </div>

                                )
                            )}

                        </div>

                    )}

                </section>


                {/* All Organisations */}

                <section className="admin-section">

                    <div className="section-header">

                        <div>
                            <h2>
                                All Organisations
                            </h2>

                            <p>
                                Overview of organisations on
                                the platform.
                            </p>
                        </div>

                    </div>


                    {!loading &&
                        organisations.length > 0 && (

                            <div className="table-container">

                                <table>

                                    <thead>
                                        <tr>
                                            <th>
                                                Organisation
                                            </th>

                                            <th>
                                                Status
                                            </th>

                                            <th>
                                                Created
                                            </th>

                                            <th>
                                                Action
                                            </th>
                                        </tr>
                                    </thead>

                                    <tbody>

                                        {organisations.map(
                                            (organisation) => (

                                                <tr
                                                    key={
                                                        organisation.id
                                                    }
                                                >

                                                    <td>
                                                        <strong>
                                                            {
                                                                organisation.name
                                                            }
                                                        </strong>
                                                    </td>

                                                    <td>

                                                        <span
                                                            className={`status-badge ${organisation.status}`}
                                                        >
                                                            {
                                                                organisation.status
                                                            }
                                                        </span>

                                                    </td>

                                                    <td>
                                                        {new Date(
                                                            organisation.created_at
                                                        ).toLocaleDateString()}
                                                    </td>

                                                    <td>

                                                        {organisation.status ===
                                                            "active" && (

                                                            <button
                                                                className="suspend-button"
                                                                onClick={() =>
                                                                    updateOrganisation(
                                                                        organisation.id,
                                                                        "suspend"
                                                                    )
                                                                }
                                                            >
                                                                Suspend
                                                            </button>

                                                        )}

                                                    </td>

                                                </tr>

                                            )
                                        )}

                                    </tbody>

                                </table>

                            </div>

                        )}

                </section>

            </main>

        </div>
    );
}

export default PlatformAdminDashboard;