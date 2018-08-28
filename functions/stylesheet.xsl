<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:preserve-space elements="*" />
  <xsl:template match="/">
    <html>

    <body>
      <h1>Test Report</h1>
      <ul style="list-style-type:none">
        <li>
          <p><strong>Failed : </strong>
            <xsl:value-of select="count(testsuites/testsuite/testcase[@isfailed='true'])" />
          </p>
          <blockquote>
            <xsl:if test="count(testsuites/testsuite/testcase[@isfailed='true']) &gt; 0">
              <xsl:element name="details">
                <xsl:element name="summary"><em>Details</em></xsl:element>
                <ul style="list-style-type:none">
                  <xsl:for-each select="testsuites/testsuite/testcase[@isfailed='true']">
                    <xsl:element name="details">
                      <xsl:attribute name="open">
                        <xsl:text>open</xsl:text>
                      </xsl:attribute>

                      <xsl:element name="summary">
                        <xsl:element name="a">
                          <xsl:attribute name="href">
                            <xsl:text>replace-me/test-runner/artifacts/</xsl:text>
                            <xsl:value-of select="./@testindex" />
                            <xsl:text>/</xsl:text>
                            <xsl:value-of select="./@jobId" />
                            <xsl:text>/</xsl:text>
                            <xsl:value-of select="./@testid" />
                            <xsl:text>.mp4</xsl:text>
                          </xsl:attribute>
                          <xsl:attribute name="target">
                            <xsl:text>_blank</xsl:text>
                          </xsl:attribute>
                          <xsl:value-of select="./@classname" />
                          <xsl:text>-</xsl:text>
                          <xsl:value-of select="./@name" /></xsl:element>
                      </xsl:element>


                      <li>
                        <xsl:element name="a">
                          <xsl:attribute name="href">
                            <xsl:text>replace-me/test-runner/artifacts/</xsl:text>
                            <xsl:value-of select="./@testindex" />
                            <xsl:text>/</xsl:text>
                            <xsl:value-of select="./@jobId" />
                            <xsl:text>/</xsl:text>
                            <xsl:value-of select="./@testid" />
                            <xsl:text>.log</xsl:text>
                          </xsl:attribute>
                          <xsl:attribute name="target">
                            <xsl:text>_blank</xsl:text>
                          </xsl:attribute>
                          <xsl:text>chrome_log</xsl:text>
                        </xsl:element>
                      </li>
                      <li>
                        <xsl:element name="a">
                          <xsl:attribute name="href">
                            <xsl:text>replace-me/test-runner/artifacts/</xsl:text>
                            <xsl:value-of select="./@testindex" />
                            <xsl:text>/</xsl:text>
                            <xsl:value-of select="./@jobId" />
                            <xsl:text>/</xsl:text>
                            <xsl:value-of select="./@testid" />
                            <xsl:text>.console.log</xsl:text>
                          </xsl:attribute>
                          <xsl:attribute name="target">
                            <xsl:text>_blank</xsl:text>
                          </xsl:attribute>
                          <xsl:text>console_log</xsl:text>
                        </xsl:element>
                      </li>
                      <li>
                        <xsl:element name="a">
                          <xsl:attribute name="href">
                            <xsl:text>replace-me/test-runner/artifacts/</xsl:text>
                            <xsl:value-of select="./@testindex" />
                            <xsl:text>/</xsl:text>
                            <xsl:value-of select="./@jobId" />
                            <xsl:text>/</xsl:text>
                            <xsl:value-of select="./@testid" />
                            <xsl:text>.chromedriver.log</xsl:text>
                          </xsl:attribute>
                          <xsl:attribute name="target">
                            <xsl:text>_blank</xsl:text>
                          </xsl:attribute>
                          <xsl:text>chromedriver_log</xsl:text>
                        </xsl:element>
                      </li>
                      <li>
                        <xsl:element name="a">
                          <xsl:attribute name="href">
                            <xsl:text>https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logEventViewer:group=</xsl:text>
                            <xsl:value-of select="./@loggroupid" />
                            <xsl:text>;stream=</xsl:text>
                            <xsl:value-of select="./@logstreamname" /></xsl:attribute>
                          <xsl:attribute name="target">
                            <xsl:text>_blank</xsl:text>
                          </xsl:attribute>
                          <xsl:text>cloudwatch_log</xsl:text>
                        </xsl:element>
                      </li>
                      <xsl:for-each select="current()/failure">
                        <li>
                          <p>
                            <pre><xsl:value-of select="current()/@message"/></pre>
                          </p>
                        </li>
                        <li>
                          <p>
                            <pre><xsl:value-of select="current()/text()"/></pre>
                          </p>
                        </li>

                      </xsl:for-each>
                    </xsl:element>
                  </xsl:for-each>

                </ul>
              </xsl:element>
            </xsl:if>
          </blockquote>
        </li>
        <li>
          <p><strong>Passed : </strong>
            <xsl:value-of select="count(testsuites/testsuite/testcase[@ispassed='true'])" />
          </p>
          <blockquote>
            <xsl:if test="count(testsuites/testsuite/testcase[@ispassed='true']) &gt; 0">
              <xsl:element name="details">
                <xsl:element name="summary"><em>Details</em></xsl:element>
                <ul style="list-style-type:none">
                  <xsl:for-each select="testsuites/testsuite/testcase[@ispassed='true']">
                    <xsl:element name="details">
                      <xsl:attribute name="open">
                        <xsl:text>open</xsl:text>
                      </xsl:attribute>

                      <xsl:element name="summary">
                        <xsl:element name="a">
                          <xsl:attribute name="href">
                            <xsl:text>replace-me/test-runner/artifacts/</xsl:text>
                            <xsl:value-of select="./@testindex" />
                            <xsl:text>/</xsl:text>
                            <xsl:value-of select="./@jobId" />
                            <xsl:text>/</xsl:text>
                            <xsl:value-of select="./@testid" />
                            <xsl:text>.mp4</xsl:text>
                          </xsl:attribute>
                          <xsl:attribute name="target">
                            <xsl:text>_blank</xsl:text>
                          </xsl:attribute>
                          <xsl:value-of select="./@classname" />
                          <xsl:text>-</xsl:text>
                          <xsl:value-of select="./@name" /></xsl:element>
                      </xsl:element>


                      <li>
                        <xsl:element name="a">
                          <xsl:attribute name="href">
                            <xsl:text>replace-me/test-runner/artifacts/</xsl:text>
                            <xsl:value-of select="./@testindex" />
                            <xsl:text>/</xsl:text>
                            <xsl:value-of select="./@jobId" />
                            <xsl:text>/</xsl:text>
                            <xsl:value-of select="./@testid" />
                            <xsl:text>.log</xsl:text>
                          </xsl:attribute>
                          <xsl:attribute name="target">
                            <xsl:text>_blank</xsl:text>
                          </xsl:attribute>
                          <xsl:text>chrome_log</xsl:text>
                        </xsl:element>
                      </li>
                      <li>
                        <xsl:element name="a">
                          <xsl:attribute name="href">
                            <xsl:text>replace-me/test-runner/artifacts/</xsl:text>
                            <xsl:value-of select="./@testindex" />
                            <xsl:text>/</xsl:text>
                            <xsl:value-of select="./@jobId" />
                            <xsl:text>/</xsl:text>
                            <xsl:value-of select="./@testid" />
                            <xsl:text>.console.log</xsl:text>
                          </xsl:attribute>
                          <xsl:attribute name="target">
                            <xsl:text>_blank</xsl:text>
                          </xsl:attribute>
                          <xsl:text>console_log</xsl:text>
                        </xsl:element>
                      </li>
                      <li>
                        <xsl:element name="a">
                          <xsl:attribute name="href">
                            <xsl:text>replace-me/test-runner/artifacts/</xsl:text>
                            <xsl:value-of select="./@testindex" />
                            <xsl:text>/</xsl:text>
                            <xsl:value-of select="./@jobId" />
                            <xsl:text>/</xsl:text>
                            <xsl:value-of select="./@testid" />
                            <xsl:text>.chromedriver.log</xsl:text>
                          </xsl:attribute>
                          <xsl:attribute name="target">
                            <xsl:text>_blank</xsl:text>
                          </xsl:attribute>
                          <xsl:text>chromedriver_log</xsl:text>
                        </xsl:element>
                      </li>
                      <li>
                        <xsl:element name="a">
                          <xsl:attribute name="href">
                            <xsl:text>https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logEventViewer:group=</xsl:text>
                            <xsl:value-of select="./@loggroupid" />
                            <xsl:text>;stream=</xsl:text>
                            <xsl:value-of select="./@logstreamname" /></xsl:attribute>
                          <xsl:attribute name="target">
                            <xsl:text>_blank</xsl:text>
                          </xsl:attribute>
                          <xsl:text>cloudwatch_log</xsl:text>
                        </xsl:element>
                      </li>
                    </xsl:element>
                  </xsl:for-each>

                </ul>
              </xsl:element>
            </xsl:if>
          </blockquote>
        </li>
         <li>
          <p><strong>Expired : </strong>
            <xsl:value-of select="count(testsuites/testsuite/testcase[@isexpired='true'])" />
          </p>
          <blockquote>
            <xsl:if test="count(testsuites/testsuite/testcase[@isexpired='true']) &gt; 0">
              <xsl:element name="details">
                <xsl:element name="summary"><em>Details</em></xsl:element>
                <ul style="list-style-type:none">
                  <xsl:for-each select="testsuites/testsuite/testcase[@isexpired='true']">
                    <xsl:element name="details">
                      <xsl:attribute name="open">
                        <xsl:text>open</xsl:text>
                      </xsl:attribute>

                      <xsl:element name="summary">
                        <xsl:element name="a">
                          <xsl:attribute name="href">
                            <xsl:text>replace-me/test-runner/artifacts/</xsl:text>
                            <xsl:value-of select="./@testindex" />
                            <xsl:text>/</xsl:text>
                            <xsl:value-of select="./@jobId" />
                            <xsl:text>/</xsl:text>
                            <xsl:value-of select="./@testid" />
                            <xsl:text>.mp4</xsl:text>
                          </xsl:attribute>
                          <xsl:attribute name="target">
                            <xsl:text>_blank</xsl:text>
                          </xsl:attribute>
                          <xsl:value-of select="./@classname" />
                          <xsl:text>-</xsl:text>
                          <xsl:value-of select="./@name" /></xsl:element>
                      </xsl:element>

                      <li>
                        <xsl:element name="a">
                          <xsl:attribute name="href">
                            <xsl:text>replace-me/test-runner/artifacts/</xsl:text>
                            <xsl:value-of select="./@testindex" />
                            <xsl:text>/</xsl:text>
                            <xsl:value-of select="./@jobId" />
                            <xsl:text>/</xsl:text>
                            <xsl:value-of select="./@testid" />
                            <xsl:text>.console.log</xsl:text>
                          </xsl:attribute>
                          <xsl:attribute name="target">
                            <xsl:text>_blank</xsl:text>
                          </xsl:attribute>
                          <xsl:text>console_log</xsl:text>
                        </xsl:element>
                      </li>
                      <li>
                        <xsl:element name="a">
                          <xsl:attribute name="href">
                            <xsl:text>https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logEventViewer:group=</xsl:text>
                            <xsl:value-of select="./@loggroupid" />
                            <xsl:text>;stream=</xsl:text>
                            <xsl:value-of select="./@logstreamname" /></xsl:attribute>
                          <xsl:attribute name="target">
                            <xsl:text>_blank</xsl:text>
                          </xsl:attribute>
                          <xsl:text>cloudwatch_log</xsl:text>
                        </xsl:element>
                      </li>
                    </xsl:element>
                  </xsl:for-each>

                </ul>
              </xsl:element>
            </xsl:if>
          </blockquote>
        </li>
        <li>
          <p><strong>Skipped : </strong>
            <xsl:value-of select="count(testsuites/testsuite/testcase[@isskipped='true'])" />
          </p>
          <blockquote>
            <xsl:if test="count(testsuites/testsuite/testcase[@isskipped='true']) &gt; 0">
              <xsl:element name="details">
                <xsl:element name="summary"><em>Details</em></xsl:element>
                <ul style="list-style-type:none">
                  <xsl:for-each select="testsuites/testsuite/testcase[@isskipped='true']">
                    <xsl:element name="details">
                      <xsl:attribute name="open">
                        <xsl:text>open</xsl:text>
                      </xsl:attribute>

                      <xsl:element name="summary">
                        <xsl:element name="a">
                          <xsl:attribute name="href">
                            <xsl:text>replace-me/test-runner/artifacts/</xsl:text>
                            <xsl:value-of select="./@testindex" />
                            <xsl:text>/</xsl:text>
                            <xsl:value-of select="./@jobId" />
                            <xsl:text>/</xsl:text>
                            <xsl:value-of select="./@testid" />
                            <xsl:text>.mp4</xsl:text>
                          </xsl:attribute>
                          <xsl:attribute name="target">
                            <xsl:text>_blank</xsl:text>
                          </xsl:attribute>
                          <xsl:value-of select="./@classname" />
                          <xsl:text>-</xsl:text>
                          <xsl:value-of select="./@name" /></xsl:element>
                      </xsl:element>

                      <li>
                        <xsl:element name="a">
                          <xsl:attribute name="href">
                            <xsl:text>replace-me/test-runner/artifacts/</xsl:text>
                            <xsl:value-of select="./@testindex" />
                            <xsl:text>/</xsl:text>
                            <xsl:value-of select="./@jobId" />
                            <xsl:text>/</xsl:text>
                            <xsl:value-of select="./@testid" />
                            <xsl:text>.console.log</xsl:text>
                          </xsl:attribute>
                          <xsl:attribute name="target">
                            <xsl:text>_blank</xsl:text>
                          </xsl:attribute>
                          <xsl:text>console_log</xsl:text>
                        </xsl:element>
                      </li>
                      <li>
                        <xsl:element name="a">
                          <xsl:attribute name="href">
                            <xsl:text>https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logEventViewer:group=</xsl:text>
                            <xsl:value-of select="./@loggroupid" />
                            <xsl:text>;stream=</xsl:text>
                            <xsl:value-of select="./@logstreamname" /></xsl:attribute>
                          <xsl:attribute name="target">
                            <xsl:text>_blank</xsl:text>
                          </xsl:attribute>
                          <xsl:text>cloudwatch_log</xsl:text>
                        </xsl:element>
                      </li>
                    </xsl:element>
                  </xsl:for-each>

                </ul>
              </xsl:element>
            </xsl:if>
          </blockquote>
        </li>
        <li>
          <p><strong>Total : </strong>
            <xsl:value-of select="count(testsuites/testsuite/testcase)" />
          </p>
        </li>
      </ul>






    </body>

    </html>
  </xsl:template>
</xsl:stylesheet>
