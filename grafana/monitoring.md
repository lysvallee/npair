# Monitoring Setup for 3D Model Generation Application

## Overview

This document outlines our monitoring setup for the 3D model generation application using Grafana. It covers the metrics we track, alert thresholds, technical choices, and the installation and configuration process.

## Metrics and Alert Thresholds

We focus on two primary criteria for our application: speed and reliability. The following metrics are collected for our three main APIs (data, model, user):

1. **Response Time**
   - Warning threshold: > 500 ms
   - Critical threshold: > 1000 ms

   Rationale: For a modern web application using FastAPI, known for its speed, a response time under 500 ms is considered good. Beyond 500 ms, user experience starts to degrade, and beyond 1 second, it becomes problematic.

2. **HTTP Status Codes**
   We monitor the following status codes:
   - 200 (OK)
   - 201 (Created)
   - 301 (Moved Permanently)
   - 400 (Bad Request)
   - 401 (Unauthorized)
   - 403 (Forbidden)
   - 404 (Not Found)
   - 500 (Internal Server Error)
   - 502 (Bad Gateway)
   - 503 (Service Unavailable)

   Alert: We've set up alerts specifically for 500 (Internal Server Error) codes, as these indicate critical server-side issues.

## Technical Choices for Monitoring

We chose Grafana as our monitoring solution for several key reasons:

1. **Open-source and Community Support**: Grafana is widely adopted and backed by an active community, ensuring reliability and continuous evolution.

2. **Flexibility**: It easily integrates with various data sources, including metrics specific to our FastAPI application.

3. **Powerful Visualization**: Grafana offers customizable and powerful visualization capabilities, essential for quickly interpreting the performance of our 3D modeling application.

4. **Advanced Alerting**: Its advanced alerting features allow us to respond promptly to potential issues.

### Logging Metrics

Our FastAPI service is configured to log relevant metrics during execution, including response times, HTTP status codes, and metrics specific to our 3D model generation process. These monitoring data are stored in our existing PostgreSQL database, centralizing both application data and performance metrics.

### Grafana Integration

Grafana uses its native PostgreSQL plugin to connect directly to our database, efficiently querying the stored metric data without additional intermediate tools.

### Dashboard and Alert Configuration

Custom dashboards in Grafana display key metrics using graphs, gauges, and other customizable visualizations. We've set up specific panels to monitor FastAPI performance, 3D model generation process efficiency, and overall application health.

Grafana's alerting system continuously monitors these metrics. When a predefined threshold is exceeded (e.g., excessive response time or abnormal error rate), Grafana triggers alerts. These alerts are sent to our dedicated Slack channel for rapid, targeted response.

Slack Details:
- Workspace: NPAIR
- URL: https://npair-workspace.slack.com
- Channel: #3d-model-generation

## Installation and Configuration

### Dependencies

To set up our monitoring system, you'll need:

1. Docker and Docker Compose
2. Access to our Docker images repository
3. PostgreSQL database (already part of our setup)

### Installation Steps

1. Ensure Docker and Docker Compose are installed on your system.

2. Clone our project repository.

3. In the project directory, locate the Docker Compose files. They include the Grafana service configuration.
Start the services using Docker Compose as described in the main Readme file.


### Configuration Steps

1. Access the Grafana web interface at `http://localhost:3000`. Log in as an admin.

2. Add PostgreSQL as a data source:
   - Go to Configuration > Data Sources
   - Click "Add data source" and select PostgreSQL
   - Configure the connection details to match your PostgreSQL setup

3. Import or create dashboards:
   - Go to Create > Import
   - Either upload a JSON file with predefined dashboards or create new ones

4. Set up alerts:
   - In each dashboard panel, you can configure alerts based on the metrics
   - Define conditions for response time and error rate alerts

5. Configure Slack notifications:
   - In Alerting > Notification channels, add a new Slack channel
   - Use the webhook URL for the #3d-model-generation channel in the NPAIR workspace

By following these steps, you'll have a fully functional monitoring setup for our 3D model generation application using Grafana.
