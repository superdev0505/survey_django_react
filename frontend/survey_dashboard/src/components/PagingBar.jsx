import React from 'react';
import Pagination from "react-bootstrap/Pagination";


export default class PagingBar extends React.Component {

    render() {
        const {skip, size, total, onPrevClick, onNextClick} = this.props;
        let to = skip + size;
        if (to > total) {
            to = total;
        }

        return <Pagination>
            <Pagination.Prev onClick={() => onPrevClick(skip - size <= 0 ? 0: skip - size)} />
            {skip} of {total}
            <Pagination.Next  onClick={() => onNextClick(skip + size > total ? total : size)} />
        </Pagination>;
    }

}