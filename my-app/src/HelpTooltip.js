import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import HelpOutlineIcon from '@material-ui/icons/HelpOutline';
import Tooltip from '@material-ui/core/Tooltip';

const useStyles = makeStyles((theme) => ({
  helpIcon: {
    color: theme.palette.grey[500],
    fontSize: '1.2rem',
    cursor: 'help',
    marginLeft: '5px',
  },
}));

const HelpTooltip = ({ helpText }) => {
  const classes = useStyles();

  return (
    <Tooltip title={helpText}>
      <HelpOutlineIcon className={classes.helpIcon} />
    </Tooltip>
  );
};

export default HelpTooltip;