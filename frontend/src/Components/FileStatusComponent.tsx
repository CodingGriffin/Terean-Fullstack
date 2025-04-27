// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-nocheck
import loadingGif from "./Images/loading_icon.gif"
import errorX from "./Images/error_x.png"
import greenCheck from "./Images/green_check.png"

export default function RecordStatusComponent({recordObj, height, width}) {
    if (recordObj.status === "Complete") {
        return (
            <img src={greenCheck} alt="Complete" style={{height:height, width:width}}/>
        )
    } else if (recordObj.status === "Initializing" || recordObj.status === "Loading") {
        return (
            <img src={loadingGif} alt="Loading" style={{height:height, width:width}}/>
        )
    } else if (recordObj.status === "Error") {
        return (
            <img src={errorX} alt="Error" style={{height:height, width:width}}/>
        )
    }
}