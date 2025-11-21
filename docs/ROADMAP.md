# Roadmap

This document outlines the phased development plan for AutoFactoryScope, from MVP to enterprise-ready system.

## Phase 1: MVP (Current)

**Goal:** Working ONNX inference backend with WPF desktop client and basic CI/CD.

### Milestones

- [x] Backend architecture and FastAPI setup
- [x] ONNX Runtime integration with YOLOv8 model
- [x] Image tiling and coordinate merging
- [x] Non-Maximum Suppression (NMS) implementation
- [x] Visualization and annotated image generation
- [x] WPF desktop client with image upload
- [x] Basic CI workflows (backend tests, frontend build)
- [ ] Backend unit tests and smoke tests
- [ ] Documentation (architecture, contributing, branching)

### Key Deliverables

- Functional robot detection API
- WPF client that can upload images and display results
- GitHub Actions CI for backend and frontend
- Developer documentation and contribution guidelines

**Target:** End of Phase 1 - developers can clone, set up, and run the system locally.

---

## Phase 2: Enhanced Client & Batch Processing

**Goal:** Replace WPF with web dashboard, add batch processing, and improve reporting.

### Milestones

- [ ] Web dashboard (React, Blazor, or Vue)
  - Image upload and drag-and-drop
  - Real-time detection progress
  - Interactive result visualization
  - Export annotated images and reports
- [ ] Batch processing endpoint
  - Accept multiple layout images
  - Process in parallel or queue
  - Return aggregated statistics
- [ ] Report generation
  - PDF reports with detection summaries
  - CSV export of detection data
  - Comparison reports for multiple layouts
- [ ] Performance optimizations
  - Async processing for large images
  - Caching of model and intermediate results
  - Progress tracking via WebSocket or polling

### Key Deliverables

- Web-based dashboard replacing WPF
- Batch processing API
- Automated report generation
- Improved user experience and performance

**Target:** End of Phase 2 - production-ready web application with batch capabilities.

---

## Phase 3: Advanced Features & Enterprise Scale

**Goal:** Robot classification, clustering, and support for enterprise-scale datasets.

### Milestones

- [ ] Robot type classification
  - Extend model to classify robot types (articulated, SCARA, delta, etc.)
  - Update training pipeline and model export
  - Add classification to API response
- [ ] Symbol clustering and grouping
  - Group nearby robots into workstations
  - Detect robot clusters and patterns
  - Spatial analysis and layout optimization suggestions
- [ ] Enterprise-scale support
  - Database integration for result storage
  - User authentication and authorization
  - Multi-tenant support
  - API rate limiting and quotas
- [ ] Advanced analytics
  - Historical detection trends
  - Layout comparison and diff visualization
  - Robot density heatmaps
  - Integration with factory planning tools
- [ ] Model improvements
  - Continuous learning pipeline
  - Model versioning and A/B testing
  - Performance benchmarking suite

### Key Deliverables

- Multi-class robot detection
- Spatial analysis and clustering
- Enterprise-ready infrastructure
- Advanced analytics dashboard

**Target:** End of Phase 3 - enterprise-grade system with advanced ML capabilities.

---

## Future Considerations

- **Mobile app**: Native iOS/Android apps for field engineers
- **CAD integration**: Direct import from AutoCAD, SolidWorks, etc.
- **Real-time processing**: Video stream analysis for live factory monitoring
- **Edge deployment**: ONNX Runtime on edge devices for on-premise inference
- **Federated learning**: Collaborative model training across multiple factories

---

## Versioning Strategy

- **v0.1.x**: Phase 1 MVP (current)
- **v0.2.x**: Phase 2 enhancements
- **v1.0.0**: Production-ready release (end of Phase 2)
- **v2.0.0**: Enterprise features (Phase 3)

---

## Contributing to the Roadmap

If you have ideas for features or improvements:

1. Check `docs/PROJECT_STATUS.md` to see if it's already planned
2. Open a feature request in `.github/ISSUE_TEMPLATE/feature_request.md`
3. Discuss with maintainers before starting large features
4. Follow the branching strategy in `docs/BRANCHING_STRATEGY.md`

