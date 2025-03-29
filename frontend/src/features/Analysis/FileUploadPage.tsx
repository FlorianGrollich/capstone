import React from "react";
import {useDispatch} from "react-redux";
import {setFile} from "./slices/fileUploadSlice.ts";

const FileUploadPage: React.FC = () => {
    const dispatch = useDispatch();

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files ? event.target.files[0] : null;
        dispatch(setFile(file));
    };

    return (
        <div className={"h-full px-10"}>
            <div
                className={"w-full border-2 rounded-lg border-gray-400 border-dotted h-3/6 flex items-center justify-center"}>
                <div className={"text-center text-gray-400"}>
                    <p>Upload Video Scene</p>
                    <input type="file" onChange={handleFileChange}/>
                </div>
            </div>
        </div>
    );
};

export default FileUploadPage;