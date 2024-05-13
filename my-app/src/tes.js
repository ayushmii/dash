import React, { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";
import { Modal, Button, Form } from "react-bootstrap";
import "bootstrap/dist/css/bootstrap.min.css";

function App() {
  console.log(process.env.DISEASE_APP_PORT);
  const [latestRecords, setLatestRecords] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    shortDesc: "",
    dateFrom: "",
    dateTo: "",
    diseaseNames: "",
  });
  const [recordType, setRecordType] = useState("completed");
  useEffect(() => {
    console.log(latestRecords);
  }, [latestRecords]);

  useEffect(() => {
    fetchLatestRecords(recordType);
  }, [recordType]);

  const fetchLatestRecords = async (type) => {
    try {
      const response = await axios.get(
        `http://localhost:5354/latest_records_${type}`
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

  const handleModalClose = () => {
    setShowModal(false);
  };
  const handleAddDisease = () => {
    const newDiseaseName = prompt("Enter the new disease name:");
    if (newDiseaseName) {
      setFormData((prevFormData) => ({
        ...prevFormData,
        diseaseNames: `${
          prevFormData.diseaseNames ? `${prevFormData.diseaseNames},` : ""
        }${newDiseaseName.trim()}`,
      }));
    }
  };
  const handleProceed = async () => {
    const { shortDesc, dateFrom, dateTo, diseaseNames } = formData;
    const diseaseNameList = diseaseNames.split(",").map((name) => name.trim());

    try {
      // Add a new record to the patient_counts_info table
      const infoResponse = await axios.post(
        `http://localhost:5354/patient_counts_info`,
        {
          short_desc: shortDesc,
          data_from: dateFrom,
          data_upto: dateTo,
          status: "Processing",
        }
      );
      const newInfoId = infoResponse.data.info_id;
      console.log(newInfoId);
      // Add new records to the patient_counts_disease table
      const diseasePromises = diseaseNameList.map(
        async (diseaseName, index) => {
          const diseaseResponse = await axios.post(
            `http://localhost:5354/patient_counts_disease`,
            {
              info_id: newInfoId,
              sr_no: index + 1,
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
          return diseaseResponse.data;
        }
      );
      const newDiseaseRecords = await Promise.all(diseasePromises);

      // Call the backend API to process the disease counts
      const updatedDiseaseRecords = await Promise.all(
        diseaseNameList.map(async (diseaseName, index) => {
          try {
            const response = await axios.get(
              `http://localhost:7655/disease_counts?disease_name=${diseaseName}&date_from=${dateFrom}&date_to=${dateTo}`
            );
            const diseaseCount = response.data;
            console.log(diseaseCount);
            console.log(newDiseaseRecords);
            console.log(newInfoId);

            // Find the record to update from newDiseaseRecords
            const recordToUpdate = newDiseaseRecords.find(
              (record) =>
                record.info_id === newInfoId && record.sr_no === index + 1
            );

            console.log(recordToUpdate);
            console.log(diseaseCount);

            // Update the database with the response data
            if (recordToUpdate) {
              console.log(recordToUpdate.info_id);
              const updateResponse = await axios.put(
                `http://localhost:5354/patient_counts_disease/${recordToUpdate.info_id}`,
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

      setLatestRecords(filteredUpdatedRecords);
      setShowModal(false);
    } catch (error) {
      console.error("Error adding new records:", error);
    }
  };
  <div style={{ position: "absolute", top: 0, right: 0 }}>
    {new Date().toLocaleDateString()}
  </div>;

  const recordsTable =
    latestRecords.length > 0 ? (
      <table className="table table-striped">
        <thead>
          <tr>
            <th>ID</th>
            <th>Info ID</th>
            <th>SR No</th>
            <th>Disease Desc</th>
            <th>Disease</th>
            <th>Visits</th>
            <th>Patients</th>
            <th>Discharge Summaries</th>
            <th>DS Patients</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {latestRecords.map((record) => (
            <tr key={record.id}>
              <td>{record[0]}</td>
              <td>{record[1]}</td>
              <td>{record[2]}</td>
              <td>{record[3]}</td>
              <td>{record[4]}</td>
              <td>{record[5]}</td>
              <td>{record[6]}</td>
              <td>{record[7]}</td>
              <td>{record[8]}</td>
              <td>{record[9]}</td>
            </tr>
          ))}
        </tbody>
      </table>
    ) : (
      <p>Loading...</p>
    );

  return (
    <div className="App">
      <h1>Patient Counts Disease</h1>
      <div>
        <button
          className="btn btn-primary mr-2"
          onClick={() => {
            setRecordType("completed");
            fetchLatestRecords("completed");
          }}
        >
          Completed Records
        </button>
        <button
          className="btn btn-primary"
          onClick={() => {
            setRecordType("processing");
            fetchLatestRecords("processing");
          }}
        >
          Processing Records
        </button>
        <div>
          <button className="btn btn-primary mr-2" onClick={handleAddDisease}>
            Add Disease
          </button>
          <button className="btn btn-primary mr-2" onClick={handleNewSearch}>
            New Search
          </button>
        </div>
      </div>
      <button className="btn btn-primary" onClick={handleNewSearch}>
        New Search
      </button>
      {recordsTable}

      <Modal show={showModal} onHide={handleModalClose}>
        <Modal.Header closeButton>
          <Modal.Title>New Search</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group controlId="formShortDesc">
              <Form.Label>Short Description</Form.Label>
              <Form.Control
                type="text"
                name="shortDesc"
                value={formData.shortDesc}
                onChange={handleInputChange}
              />
            </Form.Group>
            <Form.Group controlId="formDateFrom">
              <Form.Label>Date From</Form.Label>
              <Form.Control
                type="date"
                name="dateFrom"
                value={formData.dateFrom}
                onChange={handleInputChange}
              />
            </Form.Group>
            <Form.Group controlId="formDateTo">
              <Form.Label>Date To</Form.Label>
              <Form.Control
                type="date"
                name="dateTo"
                value={formData.dateTo}
                onChange={handleInputChange}
              />
            </Form.Group>
            <Form.Group controlId="formDiseaseNames">
              <Form.Label>Disease Names (separated by commas)</Form.Label>
              <Form.Control
                type="text"
                name="diseaseNames"
                value={formData.diseaseNames}
                onChange={handleInputChange}
              />
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleModalClose}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleProceed}>
            Proceed
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
}

export default App;
