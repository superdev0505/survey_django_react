import React from "react";
import Form from "react-bootstrap/Form";
import Button from "react-bootstrap/Button";
import API from "../../API";
import TagField from "../../components/TagField";
import Alert from "react-bootstrap/Alert";

export default class QuestionItem extends React.Component {

    state = {
        id: '',
        enabled: false,
        allTags: [],
        text: '',
        answerType: '',
        tags: [],
        choiceSet: [],
        showAlert: false,
        errorText: ''
    };

    componentDidMount() {
        this.propsToState(this.props.data)
    }

    componentDidUpdate(prevProps) {
        console.log('component did update', prevProps);
        if (this.props.data.id !== prevProps.data.id) {
            this.propsToState(this.props.data)
        }
    }

    propsToState(data) {
        let {id, text, tags, answer_type, choice_set, enabled} = data;
        this.setState({
            id,
            text: text || '',
            tags: tags || [],
            enabled: enabled || false,
            choiceSet: choice_set || [],
            answerType: answer_type || 'vote',
        })
    }

    onAddAnswer = () => {
        let {choiceSet} = this.state;
        this.setState({
            choiceSet: choiceSet.concat([{
                tags: [],
                text: '',
                isNew: true,
                id: 'tempChoice-' + (Math.random() * 10000).toFixed()
            }])
        })
    };

    onSaveQuestion = (e) => {
        let {id, text, tags, choiceSet, answerType, enabled} = this.state;
        e.preventDefault();
        API.fetch(API.QUESTIONS_SAVE, {
            id, text,
            tags: tags,
            choice_set: choiceSet.map(c => c.isNew ? {tags: c.tags, text: c.text} : c),
            answer_type: answerType,
            enabled: enabled
        }).then(data => {
            if (data.error) {
                return this.setState({errorText: data.error}, () => {
                    setTimeout(() => this.setState({errorText: ''}), 5000)
                })
            }

            this.setState({showAlert: true}, () => {
                setTimeout(() => this.setState({showAlert: false}), 2000);
                this.props.onSaveQuestion()
            });
        }).catch(error => {
            this.setState({errorText: error})
        })
    };

    onDeleteQuestion = () => {
        API.fetch(API.QUESTIONS_DELETE, {
            id: this.state.id
        })
            .then(() => this.props.onDeleteQuestion())
    };

    onFieldUpdate = (e) => {
        console.log('[AAAA]', e.target.name, e.target.value);
        if (e.target.type === 'checkbox') {
            return this.setState({[e.target.name]: e.target.checked})
        }

        this.setState({[e.target.name]: e.target.value})
    };

    onChoiceTagChange = (choice, tags) => {
        let choiceSet = this.state.choiceSet.map(c => {
            if (choice.id === c.id) {
                c.tags = tags;
                return c
            }
            return c
        });

        this.setState(choiceSet)
    };

    onChoiceTextChange = (choice, text) => {
        let choiceSet = this.state.choiceSet.map(c => {
            if (choice.id === c.id) {
                c.text = text;
                return c
            }
            return choice
        });

        this.setState(choiceSet)
    };

    render() {
        let {text, tags, answerType, choiceSet, showAlert, id, enabled, errorText} = this.state;
        let {answerTypes} = this.props;

        return <Form className="p-3">
            <h4>Question text</h4>
            <Form.Group controlId="questionText">
                <Form.Control type="text" rows="3" name="text" value={text} onChange={this.onFieldUpdate}/>
            </Form.Group>


            <div key={"question-tags-o-" + id}>
                <Form.Group key={"question-tags-" + id}>
                    <TagField id={"question-tags-" + id}
                              defaultSelected={tags}
                              onTagChange={(tags) => this.setState({tags})}/>
                </Form.Group>
            </div>

            <Form.Group>
                <Form.Label>Answer type</Form.Label>
                <Form.Control as="select" className="w-25" name="answerType" value={answerType}
                    onChange={this.onFieldUpdate}>
                    {answerTypes.map(answerType =>
                        <option value={answerType} key={answerType}>{answerType}</option>
                    )}
                </Form.Control>
            </Form.Group>

            <Form.Group>
                <Form.Check type="checkbox" controlId="questionEnabled"
                            label="Question Enabled"
                            name="enabled" checked={enabled} onChange={this.onFieldUpdate}/>
            </Form.Group>

            <br/>

            <h4>Answers</h4>
            <div>
                {choiceSet && choiceSet.map( choice => {
                    return <div key={choice.id}>
                        <Form.Group>
                            <Form.Control className="w-75" type="text" placeholder="Answer"
                                          defaultValue={choice.text}
                                          onChange={(e) => this.onChoiceTextChange(choice, e.target.value)}
                            />
                            <TagField id={"tags-" + choice.id}
                                      defaultSelected={choice.tags}
                                      onTagChange={(tags) => this.onChoiceTagChange(choice, tags)}/>
                        </Form.Group>
                    </div>
                })}
            </div>

            <div className="d-flex justify-content-between w-75 mb-5">
                <Button variant="primary" onClick={this.onAddAnswer}>Add Answer</Button>
                <div>
                    <Button variant="danger" className="mr-3" onClick={this.onDeleteQuestion}>Delete</Button>

                    <Button variant="success" onClick={this.onSaveQuestion}>Save</Button>
                </div>
            </div>

            {showAlert && <Alert variant="success" className="w-25 m-2">
                <p>
                    Question was successfully saved!
                </p>
            </Alert>}

            {errorText && <Alert variant="danger" className="w-25 m-2">
                <p>
                    {errorText}
                </p>
            </Alert>}
        </Form>
    }

}
