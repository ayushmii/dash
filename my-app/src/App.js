import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import { Modal, Button, Form, Container, Typography, Paper, TextField, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, IconButton } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import { TablePagination, TableSortLabel } from '@material-ui/core';
import HelpTooltip from './HelpTooltip.js'
import 'bootstrap/dist/css/bootstrap.min.css';
import RecordsTable from './ShowRecords';
const diseaseAppPort = process.env.REACT_APP_DISEASE_APP_PORT;
const dashboardAppPort = process.env.REACT_APP_DASHBOARD_APP_PORT;
const queryServerPort = process.env.REACT_APP_QUERY_SERVER_PORT;
const patientCountStackPort = process.env.PATIENT_COUNT_STACK_PORT;
const patientCountPort = process.env.PATIENT_COUNT_PORT;

console.log(queryServerPort)
const useStyles = makeStyles((theme) => ({
  container: {
    padding: theme.spacing(2),
    backgroundColor: 'var(--background-color)',
    color: 'var(--text-color)',
  },
  paper: {
    padding: theme.spacing(2),
    marginBottom: theme.spacing(2),
    backgroundColor: 'var(--primary-color)',
    borderRadius: '10px',
    boxShadow: '0 4px 8px rgba(0, 0, 0, 0.2)',
  },
  modal: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  modalPaper: {
    padding: theme.spacing(2),
    backgroundColor: 'var(--primary-color)',
    boxShadow: theme.shadows[5],
    outline: 'none',
    borderRadius: '10px',
  },
  button: {
    margin: theme.spacing(1),
    backgroundColor: 'var(--secondary-color)',
    color: 'var(--text-color)',
    '&:hover': {
      backgroundColor: 'var(--accent-color)',
    },
  },
  table: {
    backgroundColor: 'var(--background-color)',
  },
  tableHead: {
    backgroundColor: 'var(--primary-color)',
    color: 'var(--text-color)',
  },
  tableRow: {
    '&:nth-of-type(odd)': {
      backgroundColor: 'var(--card-hover-color)',
    },
  },
  textField: {
    '& .MuiInputBase-root': {
      color: 'var(--text-color)',
      backgroundColor: 'var(--background-color)',
      borderColor: 'var(--primary-color)',
    },
    '& .MuiInputBase-input': {
      '&::placeholder': {
        color: 'var(--placeholder-color)',
      },
    },
  },
}));

function App() {
  const classes = useStyles();
 
  const [latestRecords, setLatestRecords] = useState([]);
  const [maxSrNo, setMaxSrNo] = useState(0);
  
  const [additionalDiseaseNames, setAdditionalDiseaseNames] = useState("");
  const [infoId, setInfoId] = useState(null);

  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    shortDesc: "",
    dateFrom: "",
    dateTo: "",
    diseaseNames: "",
  });
  const handleAdditionalDiseaseNamesChange = (event) => {
    setAdditionalDiseaseNames(event.target.value);
  };
  const [recordType, setRecordType] = useState("completed");
  const [shouldRefresh, setShouldRefresh] = useState(false);
  const [shouldRefreshRecords, setShouldRefreshRecords] = useState(false);

  const handleRefreshRecords = () => {
    setShouldRefreshRecords((prevState) => !prevState);
  };
  useEffect(() => {
    // Trigger a re-render of the RecordsTable component
    setShouldRefresh((prevState) => !prevState);
  }, [infoId, latestRecords]);

  useEffect(() => {
    console.log(latestRecords);
  }, [latestRecords]);

  useEffect(() => {
    fetchLatestRecords(recordType);
  }, [recordType]);
  const formatDate = (dateStr) => {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const date = new Date(dateStr);
    const month = months[date.getMonth()];
    const year = date.getFullYear();
    return `${month} '${year.toString().slice(-2)}`;
  };
  
const formatDateNew = (dateStr) => {
  const date = new Date(dateStr);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0'); // Adding 1 to get the correct month (0-indexed)
  const day = String(date.getDate()).padStart(2, '0');
  return `${day}/${month}/${year}`;
};

  const createNewInfoRecord = async (shortDesc, dateFrom, dateTo) => {
    try {
      const infoResponse = await axios.post(
        `http://localhost:${diseaseAppPort}/patient_counts_info`,
        {
          short_desc: shortDesc,
          data_from: dateFrom,
          data_upto: dateTo,
          status: "Processing",
        }
      );
      return infoResponse.data.info_id;
    } catch (error) {
      console.error("Error creating new info record:", error);
      return null;
    }
  };
  const formatCurrentDate = () => {
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };
  const fetchLatestRecords = async (type) => {
    try {
      const response = await axios.get(
        `http://localhost:${diseaseAppPort}/latest_records_${type}`
      );
      console.log(type);
      setLatestRecords(response.data);
    } catch (error) {
      console.error(`Error fetching latest ${type} records:`, error);
    }
  };

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setFormData((prevFormData) => ({
      ...prevFormData,
      [name]: value,
    }));
  };

  const handleNewSearch = () => {
    setShowModal(true);
  };
  const handleSetInfoId = (newInfoId) => {
    setInfoId(newInfoId);
  };
  
  useEffect(() => {
    console.log('Updated infoId:', infoId);
  }, [infoId]);
  const handleModalClose = () => {
    setShowModal(false);
  };

  const [showPreviousRecordsModal, setShowPreviousRecordsModal] = useState(false);
  const [previousRecords, setPreviousRecords] = useState([]);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const [filterText, setFilterText] = useState({
    processingDate: '',
    shortDescription: '',
    disease: '',
  });
  const fetchPreviousRecords = async () => {
    try {
      console.log(diseaseAppPort)
      const response = await axios.get(`http://localhost:${diseaseAppPort}/previous_records`);
      console.log(response)
      setPreviousRecords(response.data);
      console.log(previousRecords);
    } catch (error) {
      console.error('Error fetching previous records:', error);
    }
  };
  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };
  
  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };
  const handleFilterChange = (event) => {
    setFilterText(event.target.value);
  };
  const insertRecord = async (shortDesc, dateFrom, dateTo, diseaseNames) => {
    try {
      // Add a new record to the patient_counts_info table
      const infoResponse = await axios.post(
        `http://localhost:${diseaseAppPort}/patient_counts_info`,
        {
          short_desc: shortDesc,
          data_from: dateFrom,
          data_upto: dateTo,
          status: "Processing",
        }
      );
      const newInfoId = infoResponse.data.info_id;
      setInfoId(newInfoId);
      // Add new records to the patient_counts_disease table
      const diseaseNameList = diseaseNames.split(",").map((name) => name.trim());
      const diseasePromises = diseaseNameList.map(
        async (diseaseName, index) => {
          const diseaseResponse = await axios.post(
            `http://localhost:${diseaseAppPort}/patient_counts_disease`,
            {
              info_id: newInfoId,
              sr_no: index + 1,
              disease_desc: shortDesc.toUpperCase(),
              disease: diseaseName,
              visits: null,
              patients: null,
              discharge_summaries: null,
              ds_patients: null,
              status: "Processing",
            }
          );
          console.log("DAWG")
          console.log(index);
          setMaxSrNo(index + 1);
          return diseaseResponse.data;
        }
      );
      await Promise.all(diseasePromises);
  
      // Refresh the records
      fetchLatestRecords(recordType);
    } catch (error) {
      console.error("Error inserting record:", error);
    }
  };
  const handleProceed = async () => {
    const { shortDesc, dateFrom, dateTo, diseaseNames } = formData;
    await insertRecord(shortDesc, dateFrom, dateTo, diseaseNames);
    setShowModal(false);
    setRecordType('infoid');
    console.log(latestRecords);
    console.log(maxSrNo);
  };
  const updateShortDesc = (updatedShortDesc) => {
    setFormData((prevFormData) => ({
      ...prevFormData,
      shortDesc: updatedShortDesc,
    }));
  };
  const handleProcessAdditionalDiseases = async () => {
    const { shortDesc, dateFrom, dateTo } = formData;
    const additionalDiseaseNameList = additionalDiseaseNames
      .split(",")
      .map((name) => name.trim())
      .filter((name) => name !== "");
  
    try {
      // Add a new record to the patient_counts_info table
      const newInfoId = infoId;
      console.log(newInfoId);
  
      // Add new records to the patient_counts_disease table
      const diseasePromises = additionalDiseaseNameList.map(
        async (diseaseName, index) => {
          const diseaseResponse = await axios.post(
            `http://localhost:${diseaseAppPort}/patient_counts_disease`,
            {
              info_id: newInfoId,
              sr_no: maxSrNo + index+1,
              disease_desc: shortDesc,
              disease: diseaseName,
              visits: null,
              patients: null,
              discharge_summaries: null,
              ds_patients: null,
              status: "Processing",
            }
          );
          console.log(diseaseResponse.data);
          setMaxSrNo(maxSrNo + index + 1);
          return diseaseResponse.data;
        }
      );
      const newDiseaseRecords = await Promise.all(diseasePromises);
  
      // Call the backend API to process the disease counts
      const updatedDiseaseRecords = await Promise.all(
        additionalDiseaseNameList.map(async (diseaseName, index) => {
          try {
            const response = await axios.get(
              `http://localhost:${queryServerPort}/disease_counts?disease_name=${diseaseName}&date_from=${dateFrom}&date_to=${dateTo}`
            );
            const diseaseCount = response.data;
            console.log(diseaseCount);
            console.log(newDiseaseRecords);
            console.log(newInfoId);
            console.log(index);
            // Find the record to update from newDiseaseRecords
            const recordToUpdate = newDiseaseRecords.find(
              (record) =>
                record.info_id === newInfoId && record.sr_no === maxSrNo + index + 1
            );
  
            console.log(recordToUpdate);
            console.log(diseaseCount);
  
            // Update the database with the response data
            if (recordToUpdate) {
              console.log(recordToUpdate.info_id);
              const updateResponse = await axios.put(
                `http://localhost:${diseaseAppPort}/patient_counts_disease/${recordToUpdate.info_id}`,
                {
                  sr_no: recordToUpdate.sr_no,
                  visits: diseaseCount[0].visits,
                  patients: diseaseCount[0].patients,
                  discharge_summaries: diseaseCount[0].discharge_summaries,
                  ds_patients: diseaseCount[0].ds_patients,
                }
              );
  
              // Merge the updated record with the original record
              const updatedRecord = {
                ...recordToUpdate,
                ...updateResponse.data,
              };
              return updatedRecord;
            } else {
              console.error(
                `No record found for disease: ${diseaseName} with info_id: ${newInfoId} and sr_no: ${
                  index + 1
                }`
              );
            }
          } catch (error) {
            console.error("Error processing disease counts:", error);
          }
        })
      );
  
      // Remove undefined values from the updatedDiseaseRecords array
      const filteredUpdatedRecords = updatedDiseaseRecords.filter(
        (record) => record !== undefined
      );
  
      setLatestRecords([...latestRecords, ...filteredUpdatedRecords]);
      setAdditionalDiseaseNames("");
      handleRefreshRecords();
    } catch (error) {
      console.error("Error adding new records:", error);
    }
  };

  <div style={{ position: "absolute", top: 0, right: 0 }}>
    {new Date().toLocaleDateString()}
  </div>;

    return (
      <Container className={classes.container}>
  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
    <div style={{ display: 'flex', alignItems: 'center' }}>
      <Typography variant="h3" component="h1" gutterBottom style={{ marginRight: '8px' }}>
        Disease Wise Patients counts
      </Typography>
      <Typography variant="h6" component="h2" gutterBottom>
        ({formData.shortDesc})
      </Typography>
    </div>
    <Button
      variant="contained"
      color="primary"
      className={classes.button}
      onClick={handleNewSearch}
    >
      New Search
    </Button>
    <Button
  variant="contained"
  color="primary"
  className={classes.button}
  onClick={() => {
    setShowPreviousRecordsModal(true);
    fetchPreviousRecords();
  }}
>
  Search History
</Button>
<HelpTooltip helpText="New Search for Starting New search for Disease" />
        

<Modal
  open={showPreviousRecordsModal}
  onClose={() => setShowPreviousRecordsModal(false)}
  className={classes.modal}
  aria-labelledby="previous-records-modal-title"
  aria-describedby="previous-records-modal-description"
  style={{ maxHeight: 'calc(400vh - 400px)' }}
>

  <div className={classes.modalPaper}>
    <Typography variant="h6" id="previous-records-modal-title" gutterBottom>
      Search History
    </Typography>
    <div>
          <Button
            variant="contained"
            color="primary"
            className={classes.button}
            onClick={() => {
              setRecordType('completed');
              fetchLatestRecords('completed');
              setInfoId(null);
              setShowPreviousRecordsModal(false);
            }}
          >
            Completed Searches
          </Button>
          <Button
            variant="contained"
            color="primary"
            className={classes.button}
            onClick={() => {
              setRecordType('processing');
              fetchLatestRecords('processing');
              
              setShowPreviousRecordsModal(false);
              setInfoId(null);
            }}
          >
            Processing Searches
          </Button>
          <HelpTooltip helpText="Find Search History and Filter" />
        </div>
        
    <TextField
      label="Filter by Processing Date"
      value={filterText.processingDate}
      onChange={(e) =>
        setFilterText({ ...filterText, processingDate: e.target.value })
      }
      variant="outlined"
      fullWidth
      margin="normal"
    />
    <TextField
      label="Filter by Short Description"
      value={filterText.shortDescription}
      onChange={(e) =>
        setFilterText({ ...filterText, shortDescription: e.target.value })
      }
      variant="outlined"
      fullWidth
      margin="normal"
    />
    <TextField
      label="Filter by Disease"
      value={filterText.disease}
      onChange={(e) =>
        setFilterText({ ...filterText, disease: e.target.value })
      }
      variant="outlined"
      fullWidth
      margin="normal"
    />
    <TableContainer>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>
              <TableSortLabel>Processing Date</TableSortLabel>
            </TableCell>
            <TableCell>
              <TableSortLabel>Short Description</TableSortLabel>
            </TableCell>
            <TableCell>
              <TableSortLabel>Disease</TableSortLabel>
            </TableCell>
            <TableCell></TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
  {previousRecords
    .filter(
      (record) =>
        (filterText.processingDate
          ? record[3] === filterText.processingDate
          : true) &&
        (filterText.shortDescription
          ? record[2]
            .toString()
            .toLowerCase()
            .includes(filterText.shortDescription.toLowerCase())
          : true) &&
        (filterText.disease
          ? record[1]
            .toString()
            .toLowerCase()
            .includes(filterText.disease.toLowerCase())
          : true)
    )
    .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
    .map((record) => (
      <TableRow key={record[0]}>
        <TableCell>{record[3]}</TableCell>
        <TableCell>{record[2]}</TableCell>
        <TableCell>{record[1]}</TableCell>
        <TableCell>
          <Button
            variant="contained"
            color="primary"
            onClick={() => {
              console.log(infoId);
              console.log(record[0]);
              handleSetInfoId(record[0]);
              setShowPreviousRecordsModal(false);
            }}
          >
            Search
          </Button>
        </TableCell>
      </TableRow>
    ))}
</TableBody>
      </Table>
    </TableContainer>
    <TablePagination
      rowsPerPageOptions={[10, 25, 50]}
      component="div"
      count={previousRecords.length}
      rowsPerPage={rowsPerPage}
      page={page}
      onChangePage={handleChangePage}
      onChangeRowsPerPage={handleChangeRowsPerPage}
    />
    <Button
      variant="contained"
      color="primary"
      className={classes.button}
      onClick={() => setShowPreviousRecordsModal(false)}
    >
      Close
    </Button>
  </div>
</Modal>
  </div>

        
   
        <div>
        <RecordsTable
  recordType={recordType}
  infoId={infoId}
  shouldRefresh={shouldRefresh}
  additionalDiseaseNames={additionalDiseaseNames}
  handleAdditionalDiseaseNamesChange={handleAdditionalDiseaseNamesChange}
  handleProcessAdditionalDiseases={handleProcessAdditionalDiseases}
  formData={formData}
  classes={classes}
  updateShortDesc={updateShortDesc}
  handleSetInfoId={handleSetInfoId}
/></div>
        
        
        <Modal
  open={showModal}
  onClose={handleModalClose}
  className={classes.modal}
  aria-labelledby="modal-title"
  aria-describedby="modal-description"
>
  <Paper className={classes.modalPaper}>
  <Typography variant="h6" id="modal-title" gutterBottom style={{ color: 'white' }}>
  New Search
</Typography>

    <form>
      <TextField
        label="Short Description"
        name="shortDesc"
        value={formData.shortDesc}
        onChange={handleInputChange}
        variant="outlined"
        fullWidth
        margin="normal"
      />
      <TextField
  label="Date From"
  name="dateFrom"
  type="date"
  value={formData.dateFrom}
  onChange={handleInputChange}
  variant="outlined"
  fullWidth
  margin="normal"
  InputLabelProps={{ shrink: true }}
  InputProps={{
    inputProps: {
      max: '2019-12-31', // Maximum date
      min: '2010-01-01', // Minimum date
    },
  }}
/>
<TextField
  label="Date To"
  name="dateTo"
  type="date"
  value={formData.dateTo}
  onChange={handleInputChange}
  variant="outlined"
  fullWidth
  margin="normal"
  InputLabelProps={{ shrink: true }}
  InputProps={{
    inputProps: {
      max: '2019-12-31', // Maximum date
      min: '2010-01-01', // Minimum date
    },
  }}
/>
      <TextField
        label="Disease Names (separated by commas)"
        name="diseaseNames"
        value={formData.diseaseNames}
        onChange={handleInputChange}
        variant="outlined"
        fullWidth
        margin="normal"
      />
    </form>
    <div>
      <Button
        variant="contained"
        color="primary"
        className={classes.button}
        onClick={handleProceed}
      >
        Proceed
      </Button>
      <Button
        variant="contained"
        color="secondary"
        className={classes.button}
        onClick={handleModalClose}
      >
        Cancel
      </Button>
    </div>
  </Paper>
</Modal>
      </Container>
    );
  }
  
  export default App;