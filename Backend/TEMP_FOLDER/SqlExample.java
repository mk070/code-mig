import java.sql.*;

public class SqlExample {

    public static void main(String[] args) {
        String dbConnectionString = "jdbc:postgresql://localhost:5432/cobol_db_example?user=postgres&password=password";

        try {
            Class.forName("org.postgresql.Driver");
            Connection connection = DriverManager.getConnection(dbConnectionString);
            System.out.println("Connected to database.");

            // Declare cursor for querying records
            Statement stmt = connection.createStatement();
            String sqlQuery = "SELECT ID, FIRST_NAME, LAST_NAME, PHONE, ADDRESS, IS_ENABLED, CREATE_DT, MOD_DT FROM ACCOUNTS ORDER BY ID";
            ResultSet rs = stmt.executeQuery(sqlQuery);

            // Display all accounts
            displayAllAccounts(rs);

            // Disconnect from database
            if (connection != null && connection.isClosed()) {
                connection.close();
                System.out.println("Disconnected.");
            }

        } catch (SQLException e) {
            System.out.println("SQL Error:");
            System.out.println("SQLSTATE: " + e.getSQLState());
            System.out.println("Error Message: " + e.getMessage());
            System.exit(1);
        } catch (ClassNotFoundException e) {
            System.out.println("JDBC driver not found: " + e.getMessage());
            System.exit(1);
        }
    }

    // Function to display all accounts
    public static void displayAllAccounts(ResultSet rs) {
        try {
            System.out.println("ACCOUNTS:");
            System.out.println(" ID   | First    | Last     | Phone      | Address                | Enabled ");
            System.out.println("------|----------|----------|------------|------------------------|---------");
            while (rs.next()) {
                int id = rs.getInt("ID");
                String firstName = rs.getString("FIRST_NAME");
                String lastName = rs.getString("LAST_NAME");
                String phone = rs.getString("PHONE");
                String address = rs.getString("ADDRESS");
                String isEnabled = rs.getString("IS_ENABLED");

                System.out.printf("%4d | %9s | %9s | %11s | %22s | %7s\n", id, firstName, lastName, phone, address, isEnabled);
            }
        } catch (SQLException e) {
            System.out.println("SQL Error while displaying accounts:");
            System.out.println("SQLSTATE: " + e.getSQLState());
            System.out.println("Error Message: " + e.getMessage());
            System.exit(1);
        }
    }
}