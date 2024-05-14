import React from 'react';
import { Draggable, Droppable } from 'react-beautiful-dnd';

const DraggableDiseaseList = ({ diseases, onDragEnd }) => {
  return (
    <Droppable droppableId="disease-list">
      {(provided) => (
        <ul style={{ listStyleType: 'none', padding: 0 }} ref={provided.innerRef} {...provided.droppableProps}>
          {diseases.map((disease, index) => (
            <Draggable key={index} draggableId={`disease-${index}`} index={index}>
              {(provided) => (
                <li
                  {...provided.draggableProps}
                  {...provided.dragHandleProps}
                  ref={provided.innerRef}
                  style={{
                    border: '1px solid #ccc',
                    borderRadius: '4px',
                    padding: '8px',
                    marginBottom: '4px',
                    backgroundColor: '#f9f9f9',
                    ...provided.draggableProps.style // Preserve any additional styles applied by react-beautiful-dnd
                  }}
                >
                  {disease}
                </li>
              )}
            </Draggable>
          ))}
          {provided.placeholder}
        </ul>
      )}
    </Droppable>
  );
};

export default DraggableDiseaseList;