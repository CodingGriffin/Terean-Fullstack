interface ShowPicksPageOptionsButtonProps {
  showOptions: boolean;
  setShowOptions: React.Dispatch<React.SetStateAction<boolean>>;
}

const ShowPicksPageOptionsButton: React.FC<ShowPicksPageOptionsButtonProps> = (
  {showOptions, setShowOptions}) => {

  return (
    <>
      <button
        className={`btn btn-sm ${showOptions ? "btn-outline-primary" : "btn-outline-secondary"}`}
        onClick={() => setShowOptions(!showOptions)}
      >
        {showOptions ? "Hide Options" : "Show Options"}
      </button>
    </>
  )
}

export default ShowPicksPageOptionsButton
