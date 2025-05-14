import Quick2dSForm from "../Components/Quick2dSForm.tsx";
import NavbarPageWrapper from "../Components/navbar/NavbarPageWrapper.tsx";

export default function Quick2dS() {
  return (
    <NavbarPageWrapper children={<Quick2dSForm />} />
  );
}
