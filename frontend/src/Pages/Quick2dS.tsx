import Quick2dSForm from "../Components/Quick2dSForm.tsx";
import NavbarPageWrapper from "../Components/navbar/NavbarPageWrapper.tsx";

export default function Quick2dS() {
  return (
    <NavbarPageWrapper redirectOnFail={false} children={<Quick2dSForm />} />
  );
}
