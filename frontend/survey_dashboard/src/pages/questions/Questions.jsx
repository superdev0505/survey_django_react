import React from "react";
import QuestionsList from "./QuestionsList";
import API from "../../API";
import QuestionItem from "./QuestionItem";
import {questionListRequest, questionSelectEdit} from "../../actions";
import connect from "react-redux/es/connect/connect";

class Questions extends React.Component {

    state = {
        data: [],
        activeItem: null,
        answerTypes: [],
    };

    componentDidMount() {
        this.loadAnswerTypes();
        this.props.loadQuestions();
    }

    loadAnswerTypes = () => {
        API.fetch(API.ANSWER_TYPES)
            .then(answerTypes => this.setState({answerTypes: answerTypes.map(a => a[0])}))
    };

    onDeleteQuestion = () => {
        this.props.loadQuestions();
        this.props.questionSelectEdit();
    };

    onAddQuestion = () => this.props.questionSelectEdit({
        id: null,
        text: '',
        tags: [],
        choice_set: []
    });

    render() {
        let {answerTypes} = this.state;
        let {questionList, questionActiveItem} = this.props;
        console.log('questionActiveItem', questionActiveItem)
        return <div className="d-flex h-100">
            <div className="w-25 p-2">
                <QuestionsList {...this.props}
                               data={questionList}
                               onAddQuestion={this.onAddQuestion}
                               onItemClick={activeItem => this.props.questionSelectEdit(activeItem)}/>
            </div>
            <div className="flex-grow-1">
                {questionActiveItem && <QuestionItem data={questionActiveItem} id={questionActiveItem.id} answerTypes={answerTypes}
                                             onDeleteQuestion={this.onDeleteQuestion}
                                             onSaveQuestion={this.props.loadQuestions}/>}
            </div>
        </div>
    }

}

const mapStateToProps = state => ({
    questionList: state.questions.questionList,
    questionCount: state.questions.questionCount,
    questionOffset: state.questions.questionOffset,
    questionsLoading: state.questions.questionsLoading,
    questionActiveItem: state.questions.questionActiveItem
});

const mapDispatchToProps = dispatch => ({
    loadQuestions: (query, prev, next) => dispatch(questionListRequest(query, prev, next)),
    questionSelectEdit: (question) => dispatch(questionSelectEdit(question)),
});

export default connect(mapStateToProps, mapDispatchToProps)(Questions)
