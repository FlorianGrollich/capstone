import * as React from "react";
import TextField from "../../../components/TextField.tsx";
import Button from "../../../components/Button.tsx";
import {FcGoogle} from "react-icons/fc";


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

                <Button className={"bg-white border border-gray-300 text-black w-full hover:bg-gray-100 hover:shadow-lg"}><FcGoogle
                    className="mr-2"/>Google</Button>

            </div>
        </div>
    );
};

export default LoginPage;