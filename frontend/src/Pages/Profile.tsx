import ProfileCard from "../Components/ProfileCard.tsx";
import NavbarPageWrapper from "../Components/navbar/NavbarPageWrapper.tsx";

export default function Profile() {
  return (
    <NavbarPageWrapper redirectOnFail={false} children={<ProfileCard />} />
  );
}
