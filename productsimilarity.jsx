import React, { useEffect, useState, useRef } from "react";
import { Box, Typography, CircularProgress, Paper } from "@mui/material";
import axios from "axios";
import { AgGridReact } from "ag-grid-react";

import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import "ag-grid-enterprise";

import "../styles/agrid-custom.css"; 
import { ModuleRegistry, AllCommunityModule } from 'ag-grid-community';
    
ModuleRegistry.registerModules([ AllCommunityModule ]);

const ProductSimilarity = () => {
  const [rowData, setRowData] = useState([]);
  const [loading, setLoading] = useState(true);
  const gridRef = useRef();

  useEffect(() => {
    fetchSimilarityData();
  }, []);

  const fetchSimilarityData = async () => {
    try {
      const response = await axios.get("http://localhost:5000/similarity");
      const data = response.data.matches;

      const processed = data.map((row, index) => ({
        slNo: index + 1,
        ...row,
      }));

      setRowData(processed);
    } catch (err) {
      console.error("Failed to load product similarity data", err);
    } finally {
      setLoading(false);
    }
  };

  const columnDefs = [
    {
      headerName: "Sl No",
      field: "slNo",
      width: 80,
      sortable: false,
      filter: false,
      pinned: "left",
      cellStyle: {
        backgroundColor: "#f5f5f5",
        fontWeight: "bold",
        textAlign: "center"
      },
    },
    {
      headerName: "Orion Code",
      field: "Orion Code",
      width: 150, // Fixed width instead of flex
      filter: "agTextColumnFilter",
      sortable: true,
      resizable: true,
      cellStyle: { backgroundColor: "#d4edda" },
    },
    {
      headerName: "Orion Description",
      field: "Orion Description",
      width: 250, // Fixed width to enable scrolling
      filter: "agTextColumnFilter",
      sortable: true,
      resizable: true,
    },
    {
      headerName: "SDP Code",
      field: "SDP Code",
      width: 150, // Fixed width instead of flex
      filter: "agTextColumnFilter",
      sortable: true,
      resizable: true,
      cellStyle: { backgroundColor: "#fff3cd" },
    },
    {
      headerName: "SDP Description",
      field: "SDP Description",
      width: 250, // Fixed width to enable scrolling
      filter: "agTextColumnFilter",
      sortable: true,
      resizable: true,
    },
    {
      headerName: "Similarity Score",
      field: "Similarity Score",
      width: 140,
      filter: "agNumberColumnFilter",
      sortable: true,
      resizable: true,
      type: "numericColumn",
    },
  ];

  const defaultColDef = {
    minWidth: 150, // Remove flex: 1 to enable horizontal scrolling
    filter: true,
    sortable: true,
    resizable: true,
  };

  const onGridReady = (params) => {
    gridRef.current = params.api;
    // Don't call sizeColumnsToFit here to enable horizontal scrolling
  };

  // Remove onModelUpdated to prevent forcing columns to fit
  // const onModelUpdated = () => {
  //   if (gridRef.current) {
  //     gridRef.current.sizeColumnsToFit();
  //   }
  // };

  // Remove onFirstDataRendered as well
  // const onFirstDataRendered = (params) => {
  //   params.api.sizeColumnsToFit();
  // };

  return (
    <Box p={2} pt={1}>
      <Typography variant="h5" gutterBottom>
        🔍 Product Similarity Analysis
      </Typography>

      {loading ? (
        <Box display="flex" justifyContent="center" mt={4}>
          <CircularProgress />
        </Box>
      ) : (
        <Paper elevation={3} sx={{ overflow: 'hidden' }}>
          <div 
            className="ag-theme-alpine" 
            style={{ 
              width: "100%", 
              height: "600px",
              overflow: 'hidden' // Prevent parent scrollbars
            }}
          >
            <AgGridReact
              rowData={rowData}
              columnDefs={columnDefs}
              defaultColDef={defaultColDef}
              animateRows={true}
              pagination={true}
              paginationPageSize={50}
              domLayout="normal"
              theme="legacy"
              onGridReady={onGridReady}
              suppressHorizontalScroll={false} // Ensure horizontal scroll is enabled
              suppressColumnVirtualisation={false} // Enable column virtualization
            />
          </div>
        </Paper>
      )}
    </Box>
  );
};

export default ProductSimilarity;
