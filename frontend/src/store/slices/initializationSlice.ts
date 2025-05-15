import { createSlice } from '@reduxjs/toolkit';

interface InitializationState {
  isInitialized: boolean;
}

const initialState: InitializationState = {
  isInitialized: false,
};

const initializationSlice = createSlice({
  name: 'initialization',
  initialState,
  reducers: {
    setInitialized: (state, action) => {
      state.isInitialized = action.payload;
    },
  },
});

export const { setInitialized } = initializationSlice.actions;
export default initializationSlice.reducer; 