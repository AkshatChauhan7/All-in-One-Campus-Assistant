import {
    BrowserRouter,
    Routes,
    Route,
    Navigate,
} from "react-router-dom";

import Login from "./pages/Login";
import CreateOrganisation from "./pages/CreateOrganisation";
import JoinOrganisation from "./pages/JoinOrganisation";
import PlatformAdminDashboard from "./pages/PlatformAdminDashboard";

function Dashboard() {
    return (
        <div className="placeholder-page">
            <h1>Dashboard</h1>
            <p>Dashboard will be built next.</p>
        </div>
    );
}

function App() {
    return (
        <BrowserRouter>
            <Routes>

    <Route
        path="/login"
        element={<Login />}
    />

    <Route
        path="/create-organisation"
        element={<CreateOrganisation />}
    />

    <Route
        path="/join-organisation"
        element={<JoinOrganisation />}
    />

    <Route
        path="/platform-admin"
        element={<PlatformAdminDashboard />}
    />

    <Route
        path="/dashboard"
        element={<Dashboard />}
    />

    <Route
        path="*"
        element={<Navigate to="/login" replace />}
    />

</Routes>
        </BrowserRouter>
    );
}

export default App;