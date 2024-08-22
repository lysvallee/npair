FROM grafana/grafana:8.2.0

# Copy custom configuration file if needed
# COPY grafana.ini /etc/grafana/grafana.ini

# Set environment variables if needed
# ENV GF_SECURITY_ADMIN_PASSWORD=admin

EXPOSE 3000

CMD ["grafana-server", "--homepath=/usr/share/grafana"]
