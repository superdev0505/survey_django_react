import React from "react";
import {Typeahead, AsyncTypeahead} from "react-bootstrap-typeahead";
import API from '../API';

export default class TagField extends React.Component {

    state = {
        options: [],
        defaultSelected: []
    };

    onTagChange = (tags) => {
        let {onTagChange} = this.props;

        let newTag = tags.find(tag => tag.customOption);

        if (!newTag) {
            return onTagChange(tags)
        }

        API.fetch(API.TAGS_ADD, {
            text: newTag.text
        }).then(response => {
            onTagChange(tags.map(tag => ({
                text: tag.text,
                id: (tag.customOption && tag.text === response.text) ? response.id : tag.id
            })));
            this.setState({defaultSelected: tags})
        })
    };

    render() {
        let {options} = this.state;
        let {id, defaultSelected} = this.props;

        return <AsyncTypeahead
            id={id}
            defaultSelected={defaultSelected}
            labelKey="text"
            multiple
            allowNew

            className="tags-field"
            onChange={this.onTagChange}
            placeholder="Add tags..."

            options={options}
            onSearch={search => {
                this.setState({isLoading: true});
                API.fetch(API.TAGS, { search })
                    .then(options => this.setState({
                        isLoading: false,
                        options: options.results,
                    }));
            }}/>
    }
}