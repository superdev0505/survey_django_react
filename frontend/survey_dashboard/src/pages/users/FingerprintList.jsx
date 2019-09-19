import React from "react";
import PagingTable from "../../components/PagingTable";
import Utils from "../../Utils";
import Badge from "react-bootstrap/Badge";
import API from "../../API";
import Breadcrumb from "react-bootstrap/Breadcrumb";

export default (props) =>
    <div className="m-3">

        <PagingTable
            data={props.data.fingerprint.map(f => Object.assign({date: f.date}, f.fingerprint))}
            toolbarText="Surveylist"
            serverPaging
            onRowClick={() => {}}
                config={[
                    {name: 'date', field: f => Utils.formatDateTmills(f.date)},
                    {name: 'userAgent', field: 'userAgent'},
                    {name: 'screenResolution', field: f=> f.screenResolution.join('x')},
                    {name: 'availableScreenResolution', field: f=> f.availableScreenResolution.join('x')},
                    {name: 'timezoneOffset', field: 'timezoneOffset'},
                    {name: 'timezone', field: 'timezone'},
                    {name: 'language', field: 'language'},
                    {name: 'colorDepth', field: 'colorDepth'},
                    {name: 'deviceMemory', field: 'deviceMemory'},
                    {name: 'fonts', field: f=> f.fonts.join(',')},
                    {name: 'touchSupport', field: f => String(f.touchSupport)},
                    {name: 'hardwareConcurrency', field: 'hardwareConcurrency'},
                    {name: 'webglVendorAndRenderer', field: f => String(f.webglVendorAndRenderer)},
                    {name: 'sessionStorage', field: f => String(f.sessionStorage)},
                    {name: 'localStorage', field:  f => String(f.localStorage)},
                    {name: 'indexedDb', field:  f => String(f.indexedDb)},
                    {name: 'addBehavior', field:  f => String(f.addBehavior)},
                    {name: 'openDatabase', field:  f => String(f.openDatabase)},
                    {name: 'cpuClass', field: 'cpuClass'},
                    {name: 'platform', field: 'platform'},
                    {name: 'plugins', field: 'plugins'},
                    {name: 'audio', field: 'audio'},
                    {name: 'adBlock', field: f => String(f.adBlock)},
                    {name: 'hasLiedLanguages', field: f => String(f.hasLiedLanguages)},
                    {name: 'hasLiedResolution', field: f => String(f.hasLiedResolution)},
                    {name: 'hasLiedOs', field: f => String(f.hasLiedOs)},
                    {name: 'hasLiedBrowser', field: f => String(f.hasLiedBrowser)},
            ]}
        />

    </div>