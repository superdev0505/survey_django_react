import React from "react";
import {connect} from 'react-redux'
import {userListRequest} from "../../actions";
import PagingTable from "../../components/PagingTable";
import Utils from "../../Utils";
import API from "../../API";
import Badge from "react-bootstrap/Badge";
import Button from "react-bootstrap/Button";
import InputGroup from "react-bootstrap/InputGroup";
import Form from "react-bootstrap/Form";
import Spinner from "react-bootstrap/Spinner";
import Dialog from "../../components/Dialog";
import OverlayTrigger from "react-bootstrap/OverlayTrigger";
import Popover from "react-bootstrap/Popover";
import FingerprintList from "./FingerprintList";

const SOCIAL_NETWORKS = {
    'facebook': 'fa-facebook',
    'vk-oauth2': 'fa-vk',
    'google-oauth2': 'fa-google',
    'twitter': 'fa-twitter',
    'twitch': 'fa-twitch',
    'discord': 'fa-discord'
};

class UserList extends React.Component {

    state = {
        filter: '',
        filters: {
            'activeLast24h': true,
        },
        ordering: '-survey_count',
        orderingDesc: false,
        dialogOpen: false,
        dialogTarget: {},
        fingerprintOpen: false,
        fingerprintTarget: {}
    };

    componentDidMount() {
        this.loadUsers()
    }

    loadUsers = () => this.props.loadUsers(this.state.filter, null, null, this.state.filters, this.state.ordering);

    onSearchClick = (e) => {
        if (e.keyCode === 13) {
            this.loadUsers()
        }
    };

    onFilterClick = (e) => {
        let {name} = e.target;
        let filter = this.state.filters[name];
        this.setState({filters: Object.assign(this.state.filters, {[name]: !filter})}, () => {
            console.log(this.state);
            this.loadUsers()
        })
    };

    onHeaderClick = (column) => {
        let ordering = typeof column.field === 'string' ? column.field : (column.fieldOrdering || '');
        let orderingDesc = !this.state.orderingDesc;
        this.setState({ ordering: (orderingDesc ? '-' : '') + ordering, orderingDesc}, () => {
            this.props.loadUsers(this.state.filter, null, null, this.state.filters, this.state.ordering)
        })
    };

    doBlockUser = () => {
        this.setState({dialogOpen: false});
        API.fetch(API.USER_LIST_BLOCK_USER, this.state.dialogTarget)
            .then(this.loadUsers)
    };

    getStatus = f =>
        <div>
            <div>
                currrent survey: {f.current_survey && f.current_survey.questionanswer_set.length || 0} of 10
            </div>
            <div>
                currrent survey created: {f.current_survey && Utils.formatDateTmills(f.current_survey.created)}
            </div>
        </div>;

    render() {
        let {data, count, skip, size, loadUsers, offset, dataLoading} = this.props;
        let {dialogOpen, dialogTarget, filters, fingerprintOpen, fingerprintTarget} = this.state;
        let {ref_id, first_name, last_name} = dialogTarget;
        let style = {};

        console.log('{FINGER!} ', fingerprintTarget);

        return <div className="m-3">

            <InputGroup className="mb-3">
                <Form.Control
                    placeholder="filter..."
                    onKeyDown={this.onSearchClick}
                    onChange={(e) => this.setState({filter: e.target.value})}
                />
            </InputGroup>

            <div className="d-flex">

                <InputGroup className="mb-3">
                    <Form.Check
                        name='activeLast24h'
                        label='Active last 24 hours'
                        checked={filters.activeLast24h}
                        onClick={this.onFilterClick}
                    />
                </InputGroup>

                <InputGroup className="mb-3">
                    <Form.Check
                        name='onlyBots'
                        label='Only Bots'
                        onClick={this.onFilterClick}
                    />
                </InputGroup>

                <InputGroup className="mb-3">
                    <Form.Check
                        name='onlyContradicting'
                        label='Only Contradicting'
                        onClick={this.onFilterClick}
                    />
                </InputGroup>

                <InputGroup className="mb-3">
                    <Form.Check
                        name='blockedUsers'
                        label='Blocked Users'
                        onClick={this.onFilterClick}
                    />
                </InputGroup>
            </div>

            {dataLoading ?

                <div className="d-flex justify-content-center">
                    <Spinner animation="border" role="status" className="ml-5 mt-4">
                        <span className="sr-only">Loading...</span>
                    </Spinner>
                </div> :

                <PagingTable
                    data={data}
                    toolbarText="Userlist"
                    serverPaging
                    size={size}
                    skip={offset}
                    total={count}
                    onHeaderClick={this.onHeaderClick}
                    onRowClick={(r, e) => {
                        if (e.target.type === 'button') {
                            return
                        }
                        window.open('/users/' + r.id, '__blank')
                    }}
                    onPrevClick={(skip) => loadUsers(false, false, true)}
                    onNextClick={(skip) => loadUsers(false, true)}
                    onRowsCountChange={(size) => loadUsers(skip, size)}
                    config={[
                        {name: 'RefId', field: 'ref_id', style},
                        {name: 'Provider', fieldOrdering: 'provider__name',
                            field: (f) => f.provider ? f.provider.name : '', style},
                        {name: 'SubId', fieldOrdering: 'provider_user_id',
                            field: (f) => Utils.trunc(8, f.provider_user_id), style},
                        {name: 'Joined', fieldOrdering: 'date_joined',
                            field: f => Utils.formatDateTmills(f.date_joined), style},

                        {name: 'IPs', fieldOrdering: 'ip_history', field: f =>
                            <OverlayTrigger
                                trigger="click"
                                placement="left"
                                overlay={
                                    <Popover>
                                        {f.ip_history.map(ip => <div>{Utils.formatDateTmills(ip.date)} - {ip.ip}</div>)}
                                    </Popover>
                                }>
                                <Button variant="outline-success">
                                    IPs - {f.ip_history.length}
                                </Button>
                            </OverlayTrigger>
                        },

                        {name: 'Fingerprint', fieldOrdering: 'fingerprint__count',
                            field: f =>
                                <Button onClick={() => this.setState({fingerprintOpen: true, fingerprintTarget: f})}
                                        variant={"outline-success"}>
                                    FPs - {f.fingerprint.length}
                                </Button>
                        },

                        {name: 'Questions #', fieldOrdering: 'survey__status', field: 'survey_count'},
                        {name: 'Flags', fieldOrdering: 'user_flags__date',
                            field: (f) => {
                                let flags = f.user_flags.reduce((a, v) => {
                                    a[v.key] = (a[v.key] || 0) + 1;
                                    return a
                                }, {});
                                return Object.keys(flags).map(key => <Button variant="primary">
                                    {key} <Badge variant="light">{flags[key]}</Badge>
                                </Button>)
                            }
                        },
                        {name: 'Suspended', fieldOrdering: 'user_ban_history__date',
                            field: f => f.user_ban_history && !!f.user_ban_history.length && <OverlayTrigger
                                trigger="click"
                                placement="left"
                                overlay={
                                    <Popover>
                                        {f.user_ban_history.map(i => <div>{i.reason + ' - ' + Utils.formatDateTmills(i.suspend_till)}</div>)}
                                    </Popover>
                                }>
                                <Button variant={f.is_suspended ? "danger" : "outline-success"}>
                                        {f.is_suspended ? 'Suspended' : 'Suspend History'}
                                </Button>
                            </OverlayTrigger>
                        },
                        {name: 'Block user', fieldOrdering: 'is_active',
                            field: f =>
                                <Button onClick={() => this.setState({dialogOpen: true, dialogTarget: f})}
                                    variant={f.is_active ? "outline-success" : "danger"}>
                                    {f.is_active ? 'Block' : 'Unblock'}
                                </Button>
                        }
                    ]}
                />
            }

            <Dialog
                open={dialogOpen}
                text={`Are you sure want to ${dialogTarget.is_active ? 'BLOCK' : 'UNBLOCK'} user ${ref_id} - ${first_name} ${last_name} ?`}
                title={`Block User -  ${first_name} ${last_name} - ${ref_id}`}
                handleClose={() => this.setState({dialogOpen: false})}
                handleSubmit={this.doBlockUser}
            />

            <Dialog
                scrollable
                dialogClassName="modal-90w"
                open={fingerprintOpen}
                title={`Fingerprint History - ${fingerprintTarget.ref_id}`}
                text={<FingerprintList data={fingerprintTarget}/>}
                handleClose={() => this.setState({fingerprintOpen: false})}
                handleSubmit={() => this.setState({fingerprintOpen: false})}
            />
        </div>
    }

}

const mapStateToProps = state => ({
    user: state.user,
    data: state.userList.results,
    count: state.userList.count,
    offset: state.userList.offset,
    dataLoading: state.userList.dataLoading
});

const mapDispatchToProps = dispatch => ({
    loadUsers: (query, prev, next, filters, ordering) => dispatch(userListRequest(query, prev, next, filters, ordering))
});

export default connect(mapStateToProps, mapDispatchToProps)(UserList)