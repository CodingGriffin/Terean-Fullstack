import Quick2dPForm from "../Components/Quick2dPForm.tsx";
import NavbarPageWrapper from "../Components/navbar/NavbarPageWrapper.tsx";

export default function Quick2dP() {
  return (
    <NavbarPageWrapper redirectOnFail={false} children={<Quick2dPForm />} />
  );
}
