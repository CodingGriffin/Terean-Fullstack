//@ts-nocheck
import React, {useEffect, useCallback} from 'react';
import {useParams} from 'react-router';
import {useAppDispatch} from '../../hooks/useAppDispatch';
import {saveOptionsByProjectId} from '../../store/thunks/cacheThunks';
import {savePicksByProjectId} from "../../store/thunks/cacheThunks";
import { usePicks } from '../../Contexts/PicksContext';

interface PicksSettingsSaveProps {
  className?: string;
  variant?: 'primary' | 'secondary' | 'danger' | 'success' | 'warning';
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
}

export const PicksSettingsSave: React.FC<PicksSettingsSaveProps> =
  ({
     className = 'btn-sm',
     variant = 'primary',
     size = 'md',
     fullWidth = false,
   }) => {
    const dispatch = useAppDispatch();
    const {projectId} = useParams<{ projectId: string }>();
    const [isSaving, setIsSaving] = React.useState(false);
    const { autoGeneratePicksForProject, state: { isAutoPickLoading } } = usePicks();

    const handleSave = useCallback(async () => {
      if (!projectId) {
        console.error("No project ID available");
        return;
      }

      setIsSaving(true);
      try {
        dispatch(saveOptionsByProjectId(projectId));
        dispatch(savePicksByProjectId(projectId))
      } finally {
        setIsSaving(false);
      }
    }, [dispatch, projectId]);

    const handleAutoPick = useCallback(() => {
      autoGeneratePicksForProject();
    }, [autoGeneratePicksForProject]);

    useEffect(() => {
      const handleKeyDown = (event: KeyboardEvent) => {

        if ((event.ctrlKey || event.metaKey) && event.key === 's') {
          event.preventDefault();
          handleSave();
        }
      };

      window.addEventListener('keydown', handleKeyDown);

      return () => {
        window.removeEventListener('keydown', handleKeyDown);
      };
    }, [handleSave, projectId]);

    return (
      <div className="d-flex gap-2">
        <button
          className={`btn btn-${variant} ${className}`}
          onClick={handleSave}
          disabled={isSaving}
        >
          {isSaving ? (
            <>
              <span className="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
              Saving...
            </>
          ) : (
            'Save'
          )}
        </button>
        
        <button
          className={`btn btn-outline-secondary ${className}`}
          onClick={handleAutoPick}
          disabled={isAutoPickLoading}
        >
          {isAutoPickLoading ? (
            <>
              <span className="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
              Auto Picking...
            </>
          ) : (
            'Auto Pick'
          )}
        </button>
      </div>
    );
  };

export default PicksSettingsSave;
