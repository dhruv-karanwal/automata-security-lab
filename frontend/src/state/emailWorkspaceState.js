export function createInitialEmailWorkspaceState() {
  return {
    subject: '',
    body: '',
    selectedSampleKey: '',
    mode: 'combined',
    pdfFilename: '',
    originalExtractedText: '',
    extractionNote: '',
    pageCount: 0,
    isUserEdited: false,
    isLoading: false,
    result: null,
    backendError: null,
    isOfflineDemo: false,
  };
}

const withoutAnalysis = (state) => ({
  ...state,
  result: null,
  backendError: null,
  isOfflineDemo: false,
});

export function emailWorkspaceReducer(state, action) {
  switch (action.type) {
    case 'EDIT_SUBJECT':
      return {
        ...withoutAnalysis(state),
        subject: action.value,
        selectedSampleKey: '',
      };
    case 'EDIT_BODY':
      return {
        ...withoutAnalysis(state),
        body: action.value,
        selectedSampleKey: '',
        isUserEdited: Boolean(state.originalExtractedText) && action.value !== state.originalExtractedText,
      };
    case 'PDF_EXTRACTED':
      return {
        ...withoutAnalysis(state),
        subject: '',
        body: action.payload.extracted_text,
        selectedSampleKey: '',
        pdfFilename: action.payload.filename,
        originalExtractedText: action.payload.extracted_text,
        extractionNote: action.payload.extraction_note,
        pageCount: action.payload.page_count,
        isUserEdited: false,
      };
    case 'LOAD_SAMPLE':
      return {
        ...withoutAnalysis(state),
        subject: action.sample?.subject ?? '',
        body: action.sample?.body ?? '',
        selectedSampleKey: action.sample?.id ?? '',
      };
    case 'SET_MODE':
      return {
        ...withoutAnalysis(state),
        mode: action.mode,
      };
    case 'ANALYSIS_START':
      return {
        ...state,
        isLoading: true,
        backendError: null,
        isOfflineDemo: false,
      };
    case 'ANALYSIS_SUCCESS':
      return {
        ...state,
        isLoading: false,
        result: action.result,
        backendError: null,
        isOfflineDemo: Boolean(action.isOfflineDemo),
      };
    case 'ANALYSIS_ERROR':
      return {
        ...state,
        isLoading: false,
        result: null,
        backendError: action.error,
        isOfflineDemo: false,
      };
    case 'CLEAR':
      return {
        ...state,
        subject: '',
        body: '',
        selectedSampleKey: '',
        pdfFilename: '',
        originalExtractedText: '',
        extractionNote: '',
        pageCount: 0,
        isUserEdited: false,
        isLoading: false,
        result: null,
        backendError: null,
        isOfflineDemo: false,
      };
    default:
      return state;
  }
}
