import React from 'react';
import Table from "react-bootstrap/Table";
import PagingBar from "./PagingBar";


export default class PagingTable extends React.Component {

    state = {
        sortField: '',
        sortDesc: ''
    };

    onHeaderClick(column) {
        this.setState({
            sortDesc: !this.state.sortDesc,
            sortField: column.sortField || column.field
        })
    }

    render() {
        let {data, onRowClick, onCellClick, onHeaderClick, rowColumnStyle, config, tableClassName, serverPaging} = this.props;
        let {sortField, sortDesc} = this.state;


        if (sortField) {
            data = data.sort((a,b) => {
                a = a[sortField];
                b = b[sortField];

                if (Number(a) >= 0) {
                    a = Number(a);
                    b = Number(b);
                }
                console.log('[SORT]', typeof a, typeof b);
                return a === b ? 0 : ((a < b) !== sortDesc ? -1 : 1);
            })
        }

        config = config.filter(f => !f.hidden);

        return <div className={tableClassName}>

            <Table selectable={true}
                   onCellClick={onCellClick}>

                <thead>
                <tr>
                    {config.map((c, i) =>
                        <th key={i}
                            onClick={() => onHeaderClick ? onHeaderClick(c) : this.onHeaderClick(c)}
                            style={{width: c.width, cursor: 'pointer'}}>
                                    <span>
                                        {c.name}
                                        {c.field !== this.state.sortField ? '' :
                                            this.state.sortDesc
                                                ? <i className="fa fa-angle-up"/>
                                                : <i className="fa fa-angle-down"/>
                                        }
                                    </span>
                        </th>
                    )}
                </tr>
                </thead>


                <tbody>
                {data.map((d, i) =>
                    <tr key={i} style={{cursor: 'pointer'}}
                        onClick={(e) => onRowClick && onRowClick(d, e)}>{
                        config.map((c, j) =>
                            <td key={j} style={Object.assign({width: c.width}, rowColumnStyle, c.style)}>
                                {
                                    typeof c.field === 'function' ? c.field(d, i) : d[c.field]
                                }
                            </td>
                        )
                    }
                    </tr>
                )}
                </tbody>

            </Table>

            {serverPaging && <PagingBar {...this.props}/>}

        </div>
    }

}

