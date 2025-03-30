import React from "react";
import {useDispatch, useSelector} from "react-redux";
import {selectFile, setFile, uploadFile} from "./slices/fileUploadSlice.ts";
import Button from "../../components/Button.tsx";
import {AppDispatch} from "../../store.ts";

const FileUploadPage: React.FC = () => {
    const dispatch = useDispatch<AppDispatch>();
    const file = useSelector(selectFile);

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
                    <input type="file" accept={"video/*"} onChange={handleFileChange}/>
                </div>
            </div>
            <Button
                className={"mt-4"}

                onClick={() => {
                    dispatch(uploadFile(file!));
                }}>Upload</Button>
        </div>
    );
};

export default FileUploadPage;