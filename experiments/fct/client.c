#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define PORT 5001
#define BUFFER_SIZE 1500

double get_time_diff(struct timeval start, struct timeval end) {
    return (end.tv_sec - start.tv_sec) * 1000000.0 + (end.tv_usec - start.tv_usec);
}

int main(int argc, char *argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s <server_ip> <size_in_MB>\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *server_ip = argv[1];
    int size_in_mb = atoi(argv[2]);
    if (size_in_mb <= 0) {
        fprintf(stderr, "Invalid size: must be > 0\n");
        return EXIT_FAILURE;
    }

    int total_bytes = size_in_mb * 1024 * 1024;
    char buffer[BUFFER_SIZE];
    memset(buffer, 'A', BUFFER_SIZE);

    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) {
        perror("Socket creation error");
        return EXIT_FAILURE;
    }

    struct sockaddr_in serv_addr = {
        .sin_family = AF_INET,
        .sin_port = htons(PORT),
    };

    if (inet_pton(AF_INET, server_ip, &serv_addr.sin_addr) <= 0) {
        perror("Invalid address");
        close(sock);
        return EXIT_FAILURE;
    }

    if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {
        perror("Connection failed");
        close(sock);
        return EXIT_FAILURE;
    }

    printf("Connected to server. Sending %d MB of data...\n", size_in_mb);

    struct timeval start, end;
    gettimeofday(&start, NULL);

    int bytes_sent = 0;
    while (bytes_sent < total_bytes) {
        int chunk = (total_bytes - bytes_sent < BUFFER_SIZE) ? total_bytes - bytes_sent : BUFFER_SIZE;
        int sent = send(sock, buffer, chunk, 0);
        if (sent <= 0) {
            perror("Send failed");
            break;
        }
        bytes_sent += sent;
    }

    gettimeofday(&end, NULL);
    close(sock);

    double duration = get_time_diff(start, end);
    printf("FCT: %f usec\n", duration);
    printf("Sent %d bytes\n", bytes_sent);
    printf("Throughput: %.2f MB/s\n", bytes_sent / (1024.0 * 1024.0) / (duration/1000000.0));

    return 0;
}
