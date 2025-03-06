import * as React from "react";
import Button from "../../../components/Button.tsx";
import TextField from "../../../components/TextField.tsx";


const LoginPage: React.FC = () => {
    return (
        <div>
            <Button>Login</Button>
            <div className={"w-1/2"}>
                <TextField onChange={() => {}} label={"E-Mail"} />
            </div>
        </div>
    );
};

export default LoginPage;