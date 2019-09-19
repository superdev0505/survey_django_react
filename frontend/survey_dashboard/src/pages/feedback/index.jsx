import React from "react";
import {connect} from 'react-redux'
import {userFeedbackAggregatedRequest, userFeedbackRequest} from "../../actions";
import PagingTable from "../../components/PagingTable";
import Utils from "../../Utils";

class FeedbackList extends React.Component {

    componentDidMount() {
        this.props.loadFeedbacks();
        this.props.loadAggregatedFeedbacks();
    }

    render() {
        let {data, count, dataAggregated, skip, size, loadData} = this.props;
        let style = {};

        return <div className="m-3">

            <div className="card border-primary mb-3">
                <div className="card-header">Aggregation by day</div>
                <div className="card-body">
                    <PagingTable
                        data={dataAggregated}
                        config={[
                            {name: 'Date', field: 'date'},
                            {name: 'VPN Blocked', field: 'blocked_vpn'},
                            {name: 'VPN Feedback', field: 'feedback_vpn'},
                            {name: 'Adblock Blocked', field: 'blocked_adblock'},
                            {name: 'Adblock Feedback', field: 'feedback_adblock'},
                        ]}
                    />
                </div>
            </div>

            <br/>

            <div className="card border-primary mb-3">
                <div className="card-header">All feedbacks </div>
                <div className="card-body">
                    <PagingTable
                        data={data}
                        toolbarText="Feedback List"
                        serverPaging
                        size={size}
                        skip={skip}
                        total={count}
                        onRowClick={() => {}}
                        onPrevClick={(skip) => loadData(skip, size)}
                        onNextClick={(skip) => loadData(skip, size)}
                        onRowsCountChange={(size) => loadData(skip, size)}
                        config={[
                            {name: 'Date', field: 'date', style},
                            {name: 'Type', field: 'type', style},
                            {name: 'Text', field: 'text', style},
                            {name: 'User', field: (f) => <span>{f.user.first_name} - {f.user.last_name}</span>, style},
                            {name: 'Fingerprint', field: (f) => Utils.trunc(250, f.fingerprint), style},
                        ]}
                    />
                </div>
            </div>
        </div>
    }

}

const mapStateToProps = state => ({
    user: state.user,
    data: state.feedbackList.results || [],
    count: state.feedbackList.count,
    dataAggregated: state.feedbackList.feedbackAggregatedList || [],
});

const mapDispatchToProps = dispatch => ({
    loadFeedbacks: () => dispatch(userFeedbackRequest()),
    loadAggregatedFeedbacks: () => dispatch(userFeedbackAggregatedRequest())
});

export default connect(mapStateToProps, mapDispatchToProps)(FeedbackList)