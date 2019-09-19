import React from "react";
import ListGroup from "react-bootstrap/ListGroup";
import Utils from "../../Utils";
import Form from "react-bootstrap/Form";
import Button from "react-bootstrap/Button";
import Pagination from "react-bootstrap/Pagination";
import InputGroup from "react-bootstrap/InputGroup";
import Badge from "react-bootstrap/Badge";


export default class QuestionsList extends React.Component{

    state = {
        filter: ''
    };

    onSearchClick = (e) => {
        if (e.keyCode === 13) {
            this.props.loadQuestions(this.state.filter);
        }
    };

    render() {
        let {data, onItemClick, loadQuestions, questionsLoading, questionOffset, questionCount} = this.props;
        let {filter} = this.state;

        return <div className="h-100">

            <InputGroup className="mb-3">
                <Form.Control
                    placeholder="filter..."
                    onKeyDown={this.onSearchClick}
                    onChange={(e) => this.setState({filter: e.target.value})}
                />
                <InputGroup.Append>
                    <Button variant="success" onClick={this.props.onAddQuestion}>+</Button>
                </InputGroup.Append>
            </InputGroup>

            {questionsLoading
                ? <div className="p-5 d-flex align-items-center justify-content-center">
                    <div className="spinner-border" role="status">
                        <span className="sr-only">Loading...</span>
                    </div>
                  </div>
                : <ListGroup defaultActiveKey="#link1">
                        {
                            data.map(item => {
                                return <ListGroup.Item key={item.id} action onClick={() => onItemClick(item)}>
                                    <div className="d-flex">
                                        <div className="flex-grow-1">
                                        {Utils.trunc(50, item.text)}
                                        </div>
                                        <div>
                                            {(!item.text || !!item.choice_set.filter(c=>!c.text).length) && <Badge variant="danger">Wrong</Badge>}
                                            {(!item.enabled) && <Badge variant="secondary">Disabled</Badge>}
                                        </div>
                                    </div>
                                </ListGroup.Item>
                            })
                        }
                    </ListGroup>
            }

            <Pagination>
                <Pagination.Prev onClick={() => loadQuestions(false, false, true)} />
                <Pagination.Item>from {questionOffset} to {questionOffset + 100} of {questionCount}</Pagination.Item>
                <Pagination.Next onClick={() => loadQuestions(false, true)} />
            </Pagination>
        </div>
    }
}
