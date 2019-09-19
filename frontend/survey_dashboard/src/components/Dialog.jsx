import React from 'react';
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";

export default class Dialog extends React.Component {

    render() {
        let {open, title, text, handleClose, handleSubmit, scrollable, dialogClassName, style} = this.props;

        return <Modal show={open} onHide={handleClose} scrollable={scrollable} dialogClassName={dialogClassName} style={style}>
            <Modal.Header closeButton>
                <Modal.Title>{title}</Modal.Title>
            </Modal.Header>
            <Modal.Body>{text}</Modal.Body>
            <Modal.Footer>
                <Button variant="secondary" onClick={handleClose}>
                    No
                </Button>
                <Button variant="primary" onClick={handleSubmit}>
                    Yes
                </Button>
            </Modal.Footer>
        </Modal>;
    }

}