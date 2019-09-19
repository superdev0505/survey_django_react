import React from "react";
import API from "../../API";
import Utils from "../../Utils";
import Button from "react-bootstrap/Button";
import InputGroup from "react-bootstrap/InputGroup";
import Form from "react-bootstrap/Form";
import DatePicker from "react-datepicker";
import moment from 'moment/moment'


export default class Reports extends React.Component {

    state = {
        countries: '',
        date_from: new Date(),
        date_to: new Date(),
        s_date_from: new Date(),
        s_date_to: new Date(),
    };

    onSpecificCountriesDownloadClick = () => {
        let {countries, s_date_from, s_date_to} = this.state;
        API.fetch(API.REPORT_COUNTRIES, {
            countries,
            date_from: moment(s_date_from).format('DD/MM/YYYY'),
            date_to: moment(s_date_to).format('DD/MM/YYYY'),
        })
            .then(Utils.downloadCSV)
    };

    onCountryReportDownloadClick = () => {
        let {countries, date_from, date_to} = this.state;
        date_to = moment(date_to).format('DD/MM/YYYY');
        date_from = moment(date_from).format('DD/MM/YYYY');

        this.setState({loading: true});
        API.fetch(API.REPORT_COUNTRY_AMOUNTS, { countries, date_from, date_to})
            .then((r) => {
                this.setState({loading: false});
                Utils.downloadCSV(r, `report_date_countries_${date_from}-${date_to}.csv`)
            })
    };

    handleDateChange = (date, type) => {
        this.setState({[type]: date})
    };

    render() {
        let {date_from, date_to, s_date_from, s_date_to, countries, loading} = this.state;
        let style = {};

        return <div className="m-3">

            <div className="card border-primary mb-3">
                <div className="card-header">Report by Date - Country - Mobile - Desktop, format CSV</div>
                <div className="card-body">
                    <Form noValidate>

                        <Form.Row>
                            <Form.Group className="ml-1 mr-5">
                                <Form.Label>Date From</Form.Label>
                                <div>
                                    <DatePicker
                                        selected={date_from}
                                        className="form-control"
                                        placeholderText="Click to select a date" onChange={date => this.handleDateChange(date, 'date_from')}/>
                                </div>
                            </Form.Group>
                            <Form.Group className="ml-1 mr-5">
                                <Form.Label>Date To</Form.Label>
                                <div>
                                    <DatePicker
                                        selected={date_to}
                                        className="form-control"
                                        placeholderText="Click to select a date" onChange={date => this.handleDateChange(date, 'date_to')}/>
                                </div>
                            </Form.Group>
                        </Form.Row>

                        <div className="d-flex justify-content-between w-75 my-1">
                            <Button variant="primary" onClick={this.onCountryReportDownloadClick}>
                                Download <i className={"fa " + (loading ? 'fa-sync fa-spin' : 'fa-download')} aria-hidden="true"/>
                            </Button>
                        </div>
                    </Form>
                </div>
            </div>


            <div className="card border-primary mb-3">
                <div className="card-header">Report for specific provided countries, format CSV</div>
                <div className="card-body">
                    <Form noValidate>

                        <Form.Row>
                            <Form.Group className="ml-1 mr-5">
                                <Form.Label>Date From</Form.Label>
                                <div>
                                    <DatePicker
                                        selected={s_date_from}
                                        className="form-control"
                                        placeholderText="Click to select a date" onChange={date => this.handleDateChange(date, 's_date_from')}/>
                                </div>
                            </Form.Group>
                            <Form.Group className="ml-1 mr-5">
                                <Form.Label>Date To</Form.Label>
                                <div>
                                    <DatePicker
                                        selected={s_date_to}
                                        className="form-control"
                                        placeholderText="Click to select a date" onChange={date => this.handleDateChange(date, 's_date_to')}/>
                                </div>
                            </Form.Group>
                        </Form.Row>

                        <Form.Row>
                            <InputGroup className="ml-1 my-1">
                                <Form.Control
                                    placeholder="Countries"
                                    as="textarea" rows="3"
                                    onChange={(e) => this.setState({countries: e.target.value})}
                                />
                            </InputGroup>
                        </Form.Row>


                        <div className="d-flex justify-content-between w-75 my-1">
                            <Button variant="primary" onClick={this.onSpecificCountriesDownloadClick}>
                                Download <i className="fa fa-download" aria-hidden="true"/>
                            </Button>
                        </div>
                    </Form>
                </div>
            </div>

        </div>
    }

}
