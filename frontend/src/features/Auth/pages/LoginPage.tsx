import * as React from "react";
import TextField from "../../../components/TextField.tsx";


const LoginPage: React.FC = () => {
    return (
        <div className={""}>
            <div className={"grid grid-cols-3 h-full"}>
                <div></div>
                <div className={"col-start-2 "}>
                    <TextField onChange={() => {}} label={"Email"}/>
                </div>
                <div></div>
            </div>
        </div>
    );
};

export default LoginPage;