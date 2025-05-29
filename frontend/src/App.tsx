import { Routes, Route, Navigate } from "react-router-dom";
import Login from "./Pages/Login.js";
import ProtectedPage from "./Pages/Protected.tsx";
import HomePage from "./Pages/HomePage.tsx";
import Profile from "./Pages/Profile.js";
import Logout from "./Pages/Logout.js";
import Quick2dS from "./Pages/Quick2dS.js";
import Quick2dP from "./Pages/Quick2dP.js";
import { ErrorBoundary } from "./Components/ErrorBoundary.tsx";
import ErrorPage from "./Pages/ErrorPage.tsx";
import PasswordChangePage from "./Pages/PasswordChangePage.tsx";
import ForgotPasswordPage from "./Pages/ForgotPasswordPage.tsx";
import ForbiddenPage from "./Pages/ForbiddenPage.tsx";
import ProtectedRoute from "./Components/auth/ProtectedRoute.tsx";
import ProtectedAdminRoute from "./Components/admin/ProtectedAdminRoute.tsx";
import AdminDashboardPage from "./Pages/Admin/AdminDashboardPage.tsx";
import AdminUsers from "./Pages/Admin/AdminUsersPage.tsx";
import CreateUser from "./Pages/Admin/CreateUserPage.tsx";
import UpdateUser from "./Pages/Admin/UpdateUser.tsx";
import PicksPage from "./Pages/Projects/PicksPage.tsx";
import DisperPage from "./Pages/Projects/DisperPage.tsx";
import ProjectPage from "./Pages/Projects/ProjectPage.tsx";
import ProjectsPage from "./Pages/Projects/ProjectsPage.tsx";

export default function App() {
  return (
    <ErrorBoundary>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/logout" element={<Logout />} />

        {/* Protected routes that require user to be logged in */}
        <Route
          path="/profile"
          element={
            <ProtectedRoute minAuthLevel={1}>
              <Profile />
            </ProtectedRoute>
          }
        />
        <Route
          path="/protected"
          element={
            <ProtectedRoute minAuthLevel={4}>
              <ProtectedPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/quick2dp"
          element={
            <ProtectedRoute minAuthLevel={1}>
              <Quick2dP />
            </ProtectedRoute>
          }
        />
        <Route
          path="/quick2ds"
          element={
            <ProtectedRoute minAuthLevel={1}>
              <Quick2dS />
            </ProtectedRoute>
          }
        />
        <Route
          path="/projects/:projectId/picks"
          element={
            <ProtectedRoute minAuthLevel={2}>
              <PicksPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/projects/:projectId/disper"
          element={
            <ProtectedRoute minAuthLevel={2}>
              <DisperPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/projects/:projectId"
          element={
            <ProtectedRoute minAuthLevel={2}>
              <ProjectPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/projects"
          element={
            <ProtectedRoute minAuthLevel={2}>
              <ProjectsPage />
            </ProtectedRoute>
          }
        />

        {/* Admin-only protected routes */}
        <Route
          path="/admin"
          element={
            <ProtectedAdminRoute>
              <AdminDashboardPage />
            </ProtectedAdminRoute>
          }
        />
        <Route
          path="/admin/users"
          element={
            <ProtectedAdminRoute>
              <AdminUsers />
            </ProtectedAdminRoute>
          }
        />
        <Route
          path="/admin/register_user"
          element={
            <ProtectedAdminRoute>
              <CreateUser />
            </ProtectedAdminRoute>
          }
        />
        <Route
          path="/admin/users/:username"
          element={
            <ProtectedAdminRoute>
              <UpdateUser />
            </ProtectedAdminRoute>
          }
        />

        <Route path="/password_change" element={<PasswordChangePage />} />
        <Route path="/forgot_password" element={<ForgotPasswordPage />} />

        {/* Error and access pages */}
        <Route path="/403" element={<ForbiddenPage />} />
        <Route path="/404" element={<ErrorPage />} />

        {/* Catch-all route for undefined paths */}
        <Route path="*" element={<Navigate to="/404" />} />
      </Routes>
    </ErrorBoundary>
  );
}
