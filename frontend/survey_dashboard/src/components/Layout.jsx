import React from "react";
import Header from "./Header";

export default  (props) =>
    <div className="d-flex flex-column h-100">
        <Header/>
        <div className="flex-grow-1">

            {props.children}

        </div>
    </div>