import * as React from "react";
import TextField from "../../../components/TextField.tsx";


const LoginPage: React.FC = () => {
    return (
        <div className={"h-screen bg-gradient-to-tr from-primary to-accent flex items-center justify-center"}>
            <div className="bg-white rounded-xl p-4 w-1/3">
                <TextField onChange={() => {
                }} label={"Email"}/>
                <div className="h-4"></div>
                <TextField onChange={() => {
                }} label={"Password"}/>
                <div className="relative my-4 w-full">
                    <hr className="border-t-2 border-gray-300"/>
                    <div className="absolute inset-0 flex items-center justify-center">
                        <span className="bg-white px-2 text-gray-500">or</span>
                    </div>
                </div>

            </div>
        </div>
    );
};

export default LoginPage;