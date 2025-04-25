import Navbar from "../Components/navbar/Navbar.tsx";
import LogoutHandler from "../Components/auth/LogoutHandler.tsx";

export default function Logout() {
  
  return (
    <>
      <Navbar />
      <LogoutHandler />
      <h1>Successfully Logged Out!</h1>
    </>
  );
}
