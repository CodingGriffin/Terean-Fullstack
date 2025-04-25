import {useState} from "react";

export default function FileUploader() {
    const [file, setFile] = useState(null)

    function handleFileChange(e) {
        if (e.target.files) {
            setFile(e.target.files[0])
        }
    }

    return (
        <div>
            <input type="file" onChange={handleFileChange}/>
        </div>
    );
}