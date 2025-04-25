import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { FilterMatchMode, FilterOperator } from 'primereact/api';
import { DataTable } from 'primereact/datatable';
import { Dropdown } from 'primereact/dropdown';
import { Column } from 'primereact/column';
import { InputText } from 'primereact/inputtext';
import { Calendar } from 'primereact/calendar';
import { Slider } from 'primereact/slider';
import { Button } from 'primereact/button';
import {backendUrl} from "../utils/utils.tsx";

// Utility to format the date since its running a little slow still
const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return isNaN(date) ? '' : date.toLocaleDateString('en-US');
};

export default function Table(){


    const [projects, setProjects] = useState([]);
    const [globalFilterValue, setGlobalFilterValue] = useState('');
    const [loading, setLoading] = useState(false); // Added loading state to handle search operations

    //hopefully using memo cuts down on the re-rendering
    const statusMapping = useMemo(() => ({
        not_started: 'Not Started',
        in_progress: 'In Progress',
        completed: 'Completed',
        blocked: 'Blocked',
    }), []);
    
    const priorityMapping = useMemo(() => ({
        very_low: 'Very Low',
        low: 'Low',
        medium: 'Medium',
        high: 'High',
        very_high: 'Very High',
    }), []);
    
    
     // Status and priority options for filters
     const statusOptions = Object.keys(statusMapping).map(status => ({
        label: statusMapping[status], value: status,
    }));

    const priorityOptions = Object.keys(priorityMapping).map(priority => ({
        label: priorityMapping[priority], value: priority,
    }));
    
    // Preprocess the project data (formatting dates in advance)
    const preprocessProjects = useCallback((projects) => {
        return projects.map((project) => ({
            ...project,
            survey_date_formatted: project.survey_date ? formatDate(project.survey_date) : '',
            received_date_formatted: project.received_date ? formatDate(project.received_date) : '',
        }));
    }, []);

    const getProjects = async()=>{
        setLoading(true); // Start Loading
        try{
            const req = await fetch(`${backendUrl}projects`);
            const res = await req.json();
            setProjects(preprocessProjects(res));  
        } catch(error) {
            console.log(error)
        } finally {
            setLoading(false); //End loading
        }  
    };

    useEffect(() =>{
        getProjects();
    },[]);

    const [filters, setFilters] = useState({
        global: { value: null, matchMode: FilterMatchMode.CONTAINS },
        id: { value: null, matchMode: FilterMatchMode.CONTAINS },
        name: { value: null, matchMode: FilterMatchMode.CONTAINS },
        status: { value: null, matchMode: FilterMatchMode.EQUALS },
        priority: { value: null, matchMode: FilterMatchMode.EQUALS },
        velocity: { value: null, matchMode: FilterMatchMode.BETWEEN },
        geophone_spacing: { value: null, matchMode: FilterMatchMode.BETWEEN },
        survey_date: { operator: FilterOperator.AND, constraints: [{ value: null, matchMode: FilterMatchMode.DATE_EQUALS}] },
        received_date: { operator: FilterOperator.AND, constraints: [{ value: null, matchMode: FilterMatchMode.DATE_EQUALS}] }
    });

    const filteredProjects = useMemo(() => {
        if (!globalFilterValue) return projects;

        const lowerCaseFilter = globalFilterValue.toLowerCase();

        return projects.filter(project => {
            const { id, name, status, priority, velocity, geophone_spacing, survey_date, received_date } = project;

            return (
                (id && id.toString().toLowerCase().includes(lowerCaseFilter)) ||
                (name && name.toLowerCase().includes(lowerCaseFilter)) ||
                (status && statusMapping[status]?.toLowerCase().includes(lowerCaseFilter)) ||
                (priority && priorityMapping[priority]?.toLowerCase().includes(lowerCaseFilter)) ||
                (velocity && velocity.toString().includes(lowerCaseFilter)) ||
                (geophone_spacing && geophone_spacing.toString().includes(lowerCaseFilter)) ||
                (survey_date && new Date(survey_date).toLocaleDateString('en-US').includes(lowerCaseFilter)) ||
                (received_date && new Date(received_date).toLocaleDateString('en-US').includes(lowerCaseFilter))
            );
        });
    }, [projects, globalFilterValue, statusMapping, priorityMapping]);

    const clearFilter = () => {
        setGlobalFilterValue(''); // Clear the filter
    };

    const onGlobalFilterChange = (e) => {
        const inputValue = e.target.value;
        setGlobalFilterValue(inputValue);
    };
    
    
    const renderHeader = () => {
        return (
            <div className="flex justify-center w-100 ps-20">
                <div className="position-relative flex align-items-center w-70">
                    <span className="p-input-icon-right" >
                        <InputText
                            value={globalFilterValue}
                            onChange={onGlobalFilterChange}
                            placeholder="Search Projects..."
                            style={{ width: '100%' }}   
                        />
                         <i
                            className={`pi pi-${globalFilterValue ? 'times' : 'search'} large-icon`}
                            onClick={globalFilterValue ? clearFilter : null}
                            style={{
                                cursor: globalFilterValue ? 'pointer' : 'default',
                                position: 'absolute',
                                right: '10px',
                                fontSize: '24px', // Adjust the size of the icon
                                color: '#333'
                            }}
                        />
                    </span>
                </div>
            </div>
        );
    };
    

    //status filters start here
    const statusBodyTemplate = (rowData) => {
        const status = statusMapping[rowData.status];
        return <span>{status || 'N/A'}</span>;
    };

    const statusRowFilterTemplate = (options) => {
        return (
            <Dropdown
                value={options.value}
                options={statusOptions} // Use the mapped options
                onChange={(e) => {
                    options.filterApplyCallback(e.value, options.index);
                    setGlobalFilterValue(''); // Clear global filter when dropdown changes
                }}
                placeholder="Select Status"
                className="p-column-filter"
                showClear
                style={{ minWidth: '12rem' }}
            />
        );
    };
    
    //status filters end here


    //priority filter functions begin here
    
    const priorityBodyTemplate = (rowData) => {
        const priority = priorityMapping[rowData.priority];
        return <span>{priority || 'N/A'}</span>;
    };
    
    const priorityRowFilterTemplate = (options) => {
        return (
            <Dropdown
                value={options.value}
                options={priorityOptions} // Use the mapped options
                onChange={(e) => {
                    options.filterApplyCallback(e.value);
                    setGlobalFilterValue(''); // Clear global filter when dropdown changes
                }}
                placeholder="Select Priority"
                className="p-column-filter"
                showClear
                style={{ minWidth: '12rem' }}
            />
        );
    };
    
    //priority filter functions end here
    

    //velocity filters begin here

    const maxVelocity = Math.max(...projects.map(o => o.velocity));
    const minVelocity = Math.min(...projects.map(o => o.velocity));

    const velocityBodyTemplate = (rowData) => {
        return (
            <div className="flex align-items-center gap-2">
                <span>{rowData.velocity}</span>
            </div>
        )
    };

    const velocityFilterTemplate = (options) => {
        return (
            <React.Fragment>

                <Slider value={options.value} onChange={(e) => options.filterCallback(e.value)} range className="m-3" min={Math.floor(minVelocity)} max={Math.ceil(maxVelocity)}></Slider>
                <div className="flex align-items-center justify-content-between px-10 mx-2">
                    <span>{options.value ? options.value[0] : String(Math.floor(minVelocity))}</span>
                    <span>-</span>
                    <span>{options.value ? options.value[1] : String(Math.ceil(maxVelocity))}</span>
                </div>
            </React.Fragment>
        )
    }
    //velocity filters end here


    //geophone spacing filters begin here
    const maxGeophone = Math.max(...projects.map(o => o.geophone_spacing));
    const minGeophone = Math.min(...projects.map(o => o.geophone_spacing));

    const geophoneBodyTemplate = (rowData) => {
        return (
            <div className="flex align-items-center gap-2">
                <span>{rowData.geophone_spacing}</span>
            </div>
        )
    };

    const geophoneFilterTemplate = (options) => {
        return (
            <React.Fragment>

                <Slider value={options.value} onChange={(e) => options.filterCallback(e.value)} range className="m-3" min={Math.floor(minGeophone)} max={Math.ceil(maxGeophone)}></Slider>
                <div className="flex align-items-center justify-content-between mx-2">
                    <span>{options.value ? options.value[0] : String(Math.floor(minGeophone))}</span>
                    <span>-</span>
                    <span>{options.value ? options.value[1] : String(Math.ceil(maxGeophone))}</span>
                </div>
            </React.Fragment>
        )
    }
    //geophone spacing filters end here

    //survey date filters begin here
    
    
    const surveyDateRowBodyTemplate = (rowData) => {
        const date = new Date(rowData.survey_date);
        return <span>{isNaN(date) ? 'N/A' : date.toLocaleDateString()}</span>;
    };

    const surveyDateRowFilterTemplate = (options) => {
        return (
            <Calendar
                value={options.value ? new Date(options.value + 'T00:00:00') : null}
                onChange={(e) => {
                    const selectedDate = e.value;
                    options.filterCallback(selectedDate ? selectedDate.toISOString().split('T')[0] : null);
                }}
                dateFormat="mm/dd/yy"
                placeholder="mm/dd/yyyy"
            />
        );
    };
    //survey date filters end here


    // received date filters begin here
    
    const receivedDateRowFilterTemplate = (options) => {
        return (
            <Calendar
                value={options.value ? new Date(options.value + 'T00:00:00') : null} // Add time to avoid local time conversion issues
                onChange={(e) => {
                    const selectedDate = e.value;
    
                    if (selectedDate) {
                        // Create a new UTC date object
                        const utcDate = new Date(Date.UTC(
                            selectedDate.getFullYear(),
                            selectedDate.getMonth(),
                            selectedDate.getDate()
                        ));
    
                        const formattedDate = utcDate.toISOString().split('T')[0];
                        options.filterCallback(formattedDate);
                    } else {
                        options.filterCallback(null);
                    }
                }}
                dateFormat="mm/dd/yy"
                placeholder="mm/dd/yyyy"
            />
        );
    };
    
    const receivedDateRowBodyTemplate = (rowData) => {
        const parsedDate = new Date(rowData.received_date);
        return isNaN(parsedDate.getTime()) 
            ? rowData.received_date
            : parsedDate.toLocaleDateString('en-US', { year: 'numeric', month: '2-digit', day: '2-digit' });
    };

    //received date filters end here
    
    const header = renderHeader();

    return(
        <>
            <div className='card'>
                <DataTable 
                    value={filteredProjects} 
                    filters={filters} 
                    paginator 
                    rows={10} 
                    rowsPerPageOptions={[10,20,30,50]}
                    dataKey="id"
                    filterDisplay="menu"
                    globalFilterFields={['id','name','status','priority','velocity','geophone_spacing','survey_date','received_date']}
                    header={header} 
                    removableSort 
                    emptyMessage={loading ? "Loading projects..." : "No projects found."}
                    loading={loading} // Add loading indicator to the table
                    tableStyle={{minWidth: '50rem'}}
                >
                    <Column field="id" header="#" sortable></Column>
                    <Column field="name" header="Name" sortable></Column>
                    <Column field="status"
                    filterField='status' filter filterElement={statusRowFilterTemplate} body={statusBodyTemplate} header="Status" sortable></Column>
                    <Column field="priority" filterField="priority" header="Priority" style={{ minWidth: '14rem' }} filterElement={priorityRowFilterTemplate} body={priorityBodyTemplate} sortable filter></Column>
                    <Column field="velocity" header="Velocity" filter showFilterMatchModes={false} filterElement={velocityFilterTemplate} body={velocityBodyTemplate}  sortable ></Column>
                    <Column field="geophone_spacing" header="Geophone Spacing" filter  showFilterMatchModes={false} filterElement={geophoneFilterTemplate} body={geophoneBodyTemplate} sortable></Column>
                    <Column field="survey_date" dataType='date' filter showFilterMatchModes={false} filterElement={surveyDateRowFilterTemplate} body={surveyDateRowBodyTemplate} header="Survey Date" sortable></Column>
                    <Column field="received_date" dataType='date' filter showFilterMatchModes={false} filterElement={receivedDateRowFilterTemplate} body={receivedDateRowBodyTemplate} header="Received Date" sortable></Column>
                </DataTable>
            </div>
            
        </>  
    );
};
