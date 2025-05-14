import { useEffect } from "react";
import { useAuth } from "../../Contexts/authContext";

const LogoutHandler = () => {
    const { logout } = useAuth();

    useEffect(() => {
        logout();
    }, [logout]);

    return null;
};

export default LogoutHandler;
