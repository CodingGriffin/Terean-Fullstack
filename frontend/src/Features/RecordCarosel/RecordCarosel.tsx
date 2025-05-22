import type React from "react";
import { useState, useRef, useEffect, useCallback } from "react";
import RecordCard from "./RecordCard/RecordCard";
import { useAppSelector } from "../../hooks/useAppSelector";
import { selectRecordItems } from "../../store/selectors/recordSelectors";
import Pagination from "../../Components/Pagination/Pagination";
import { useAppDispatch } from "../../hooks/useAppDispatch";
import { useParams } from "react-router-dom";
import { saveOptionsByProjectId } from "../../store/thunks/cacheThunks";
import { updateRecordOption } from "../../store/slices/recordSlice";

const CARD_WIDTH = 200;
const CARD_MARGIN = 10;
const TOTAL_CARD_WIDTH = CARD_WIDTH + CARD_MARGIN * 2;

interface RecordCarouselProps {}

const RecordCarousel: React.FC<RecordCarouselProps> = () => {
  const dispatch = useAppDispatch();
  const { projectId } = useParams();
  const records = useAppSelector(selectRecordItems);
  
  const enabledRecords = records.filter((item) => item.enabled);

  const orderedIds = records.map(record => record.id);
  
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const [visibleCards, setVisibleCards] = useState<Set<string>>(new Set());
  const [perpage, setPerpage] = useState(1);
  const [pageCount, setPageCount] = useState(1);
  const [current, setCurrent] = useState(0);
  const isScrolling = useRef(false);
  const [scrollToRecordId, setScrollToRecordId] = useState<string | null>(null);

  const handleSaveOptions = () => {
    dispatch(saveOptionsByProjectId(projectId));
  }

  const handleClearSelection = () => {
    enabledRecords.forEach((record) => {
      dispatch(
        updateRecordOption({
          id: record.id,
          enabled: false,
        })
      );
    });
  };

  useEffect(() => {
    const handleScrollToRecord = (event: CustomEvent<{ recordId: string }>) => {
      setScrollToRecordId(event.detail.recordId);
      setTimeout(() => setScrollToRecordId(null), 300);
    };

    window.addEventListener('scrollToRecord', handleScrollToRecord as EventListener);

    return () => {
      window.removeEventListener('scrollToRecord', handleScrollToRecord as EventListener);
    };
  }, []);

  const calculateBlankItems = useCallback(() => {
    const totalItems = orderedIds.length;
    const remainingItems = totalItems % perpage;
    return remainingItems === 0 ? 0 : perpage - remainingItems;
  }, [orderedIds.length, perpage]);

  const extendedOrderedIds = [
    ...orderedIds,
    ...Array(calculateBlankItems()).fill("blank"),
  ];

  useEffect(() => {
    if (!scrollContainerRef.current) return;
    const observer = new IntersectionObserver(
      (entries) => {
        setVisibleCards(prev => {
          const newVisible = new Set(prev);

          entries.forEach(entry => {
            const id = entry.target.getAttribute('data-record-id');
            if (id && id !== 'blank') {
              if (entry.isIntersecting) {
                newVisible.add(id);
              } else {
                newVisible.delete(id);
              }
            }
          });

          return newVisible;
        });
      },
      {
        root: scrollContainerRef.current,
        threshold: 0.1,
        rootMargin: '0px'
      }
    );

    const cardElements = scrollContainerRef.current.querySelectorAll('.record-card-container');
    cardElements.forEach(el => observer.observe(el));

    return () => observer.disconnect();
  }, [orderedIds]);

  const scrollToPage = useCallback((pageIndex: number) => {
    setCurrent(pageIndex);
    isScrolling.current = true;
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollTo({
        left: pageIndex * TOTAL_CARD_WIDTH * perpage,
        behavior: "smooth",
      });
    }
    setTimeout(() => {
      isScrolling.current = false;
    }, 300);
  }, [perpage]);

  const updateDimensions = useCallback(() => {
    if (scrollContainerRef.current) {
      const width = scrollContainerRef.current.clientWidth;
      const newPerPage = Math.max(1, Math.floor(width / TOTAL_CARD_WIDTH));
      setPerpage(newPerPage);
      setPageCount(Math.ceil(extendedOrderedIds.length / newPerPage));
    }
  }, [extendedOrderedIds.length]);

  useEffect(() => {
    updateDimensions();
    window.addEventListener("resize", updateDimensions);
    return () => window.removeEventListener("resize", updateDimensions);
  }, [updateDimensions]);

  useEffect(() => {
    setPageCount(Math.ceil(extendedOrderedIds.length / perpage));
  }, [perpage, extendedOrderedIds.length]);

  useEffect(() => {
    if (scrollToRecordId && scrollContainerRef.current) {
      const recordIndex = orderedIds.findIndex((r) => r === scrollToRecordId);
      if (recordIndex >= 0) {
        const pageIndex = Math.floor(recordIndex / perpage);
        scrollToPage(pageIndex);
      }
    }
  }, [scrollToRecordId, orderedIds, perpage, scrollToPage]);

  const handleScroll = useCallback(() => {
    if (isScrolling.current) return;

    if (scrollContainerRef.current) {
      const scrollLeft = scrollContainerRef.current.scrollLeft;
      const newVisibleIndex = Math.round(scrollLeft / TOTAL_CARD_WIDTH);
      const newPage = Math.floor(newVisibleIndex / perpage);

      if (newPage !== current) {
        setCurrent(newPage);
      }
    }
  }, [perpage, current]);

  useEffect(() => {
    const container = scrollContainerRef.current;
    if (container) {
      container.addEventListener("scroll", handleScroll);
      return () => container.removeEventListener("scroll", handleScroll);
    }
  }, [handleScroll]);
  
  return (
    <div className="position-relative border-primary px-1">
      {orderedIds.length === 0 ? (
        <div
          className="d-flex justify-content-center align-items-center"
          style={{ height: "200px" }}
        >
          <h5 className="text-muted">No records available</h5>
        </div>
      ) : (
        <>
          <div
            ref={scrollContainerRef}
            className="d-flex overflow-auto h-100"
            style={{
              scrollBehavior: "smooth",
              WebkitOverflowScrolling: "touch",
            }}
          >
            {extendedOrderedIds.map((recordId, index) =>
              recordId === "blank" ? (
                <div
                  key={`blank-${index}`}
                  className="record-card-container"
                  data-record-id="blank"
                  style={{
                    minWidth: `${CARD_WIDTH}px`,
                    width: `${CARD_WIDTH}px`,
                    margin: `0 ${CARD_MARGIN}px`,
                    height: "100%",
                    visibility: "hidden",
                  }}
                />
              ) : (
                <div
                  key={recordId}
                  className="record-card-container"
                  data-record-id={recordId}
                  style={{
                    minWidth: `${CARD_WIDTH}px`,
                    width: `${CARD_WIDTH}px`,
                    margin: `0 ${CARD_MARGIN}px`,
                    marginLeft: index === 0 ? "0" : `${CARD_MARGIN}px`,
                    marginRight: index === extendedOrderedIds.length - 1 ? "0" : `${CARD_MARGIN}px`,
                    height: "100%",
                  }}
                >
                  <RecordCard
                    id={recordId}
                    isVisible={visibleCards.has(recordId)}
                  />
                </div>
              )
            )}
          </div>
          <div className="d-flex justify-content-center mt-3 gap-2" style={{ height: "31px" }}>
            <Pagination 
              currentPage={current}
              totalPages={pageCount}
              onPageChange={scrollToPage}
              size="sm"
              maxVisiblePages={8}
              siblingCount={2}
              boundaryCount={1}
            />
            <button
              className="btn btn-outline-primary btn-sm h-100"
              onClick={handleSaveOptions}
            >
              Save Options
            </button>
            <button
              className="btn btn-outline-danger btn-sm h-100"
              onClick={handleClearSelection}
            >
              Clear
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default RecordCarousel;
